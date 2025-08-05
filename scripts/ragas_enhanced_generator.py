"""
RAGAS-Enhanced Synthetic Data Generation for Verityn AI
Hybrid Approach: Phase 1 Enhancement

This module enhances our existing synthetic data generation with:
1. Quality stratification (High, Medium, Low, Fail)
2. RAGAS-driven gap analysis
3. SOX control ID mapping
4. Audit evidence validation
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

# Import our existing components
from synthetic_data_generation import DocumentTemplateEngine, CompanyProfile, DocumentType
from test_synthetic_generation import MockContentGenerator

class QualityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    FAIL = "fail"

class SOXControlID(Enum):
    # SOX 302 Controls
    SOX_302_1 = "302.1"  # Management assessment of disclosure controls
    SOX_302_2 = "302.2"  # Quarterly certification procedures
    SOX_302_3 = "302.3"  # Material change evaluation
    
    # SOX 404 Controls
    SOX_404_1 = "404.1"  # Internal control over financial reporting (ICFR)
    SOX_404_2 = "404.2"  # Management assessment procedures
    SOX_404_3 = "404.3"  # External auditor attestation
    SOX_404_4 = "404.4"  # Control deficiency remediation

class RAGASEnhancedGenerator:
    """Enhanced document generator with quality levels and RAGAS integration"""
    
    def __init__(self, output_dir: str = "data/enhanced_synthetic_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create enhanced subdirectories
        for quality in QualityLevel:
            (self.output_dir / quality.value).mkdir(exist_ok=True)
            (self.output_dir / quality.value / "pdf").mkdir(exist_ok=True)
            (self.output_dir / quality.value / "csv").mkdir(exist_ok=True)
            (self.output_dir / quality.value / "json").mkdir(exist_ok=True)
        
        self.template_engine = DocumentTemplateEngine()
        self.content_generator = MockContentGenerator()
        
        # Initialize SOX control mappings
        self.sox_control_mappings = self._initialize_sox_mappings()
        
    def _initialize_sox_mappings(self) -> Dict[str, Dict]:
        """Map document types to specific SOX control IDs"""
        return {
            "access_review": {
                "primary_controls": [SOXControlID.SOX_404_1, SOXControlID.SOX_404_2],
                "secondary_controls": [SOXControlID.SOX_404_4],
                "control_objectives": [
                    "Ensure appropriate user access to financial systems",
                    "Validate segregation of duties in financial processes",
                    "Monitor privileged access to SOX-critical applications"
                ]
            },
            "financial_reconciliation": {
                "primary_controls": [SOXControlID.SOX_302_1, SOXControlID.SOX_302_2],
                "secondary_controls": [SOXControlID.SOX_302_3],
                "control_objectives": [
                    "Ensure accurate financial reconciliation procedures",
                    "Validate management review and approval processes",
                    "Document variance investigation and resolution"
                ]
            },
            "risk_assessment": {
                "primary_controls": [SOXControlID.SOX_404_1, SOXControlID.SOX_404_3],
                "secondary_controls": [SOXControlID.SOX_404_2, SOXControlID.SOX_404_4],
                "control_objectives": [
                    "Identify and assess financial reporting risks",
                    "Evaluate control design effectiveness",
                    "Monitor control operating effectiveness"
                ]
            }
        }
    
    def analyze_qa_gaps(self, qa_dataset_path: str) -> Dict[str, Any]:
        """Analyze existing Q&A pairs to identify evidence gaps using RAGAS-style analysis"""
        
        # Load existing Q&A dataset
        with open(qa_dataset_path, 'r') as f:
            qa_data = json.load(f)
        
        gap_analysis = {
            "missing_evidence_types": [],
            "insufficient_detail_areas": [],
            "quality_level_gaps": [],
            "control_coverage_gaps": [],
            "recommendations": []
        }
        
        # Analyze questions to identify missing evidence
        all_questions = []
        for dataset_key, dataset in qa_data["qa_datasets"].items():
            all_questions.extend(dataset["questions"])
        
        # Gap Analysis 1: Missing Evidence Types
        evidence_keywords = {
            "approval_workflows": ["approval", "authorize", "sign-off", "review"],
            "technical_logs": ["log", "audit trail", "system", "timestamp"],
            "validation_procedures": ["validate", "verify", "check", "confirm"],
            "exception_handling": ["exception", "error", "deviation", "variance"],
            "role_segregation": ["segregation", "duties", "role", "access level"]
        }
        
        found_evidence = set()
        for question in all_questions:
            question_text = question["question"].lower()
            for evidence_type, keywords in evidence_keywords.items():
                if any(keyword in question_text for keyword in keywords):
                    found_evidence.add(evidence_type)
        
        missing_evidence = set(evidence_keywords.keys()) - found_evidence
        gap_analysis["missing_evidence_types"] = list(missing_evidence)
        
        # Gap Analysis 2: Quality Level Coverage
        complexity_distribution = {"basic": 0, "intermediate": 0, "advanced": 0}
        for question in all_questions:
            complexity_distribution[question["complexity"]] += 1
        
        total_questions = len(all_questions)
        if complexity_distribution["basic"] / total_questions > 0.5:
            gap_analysis["quality_level_gaps"].append("Too many basic questions - need more complex scenarios")
        
        if complexity_distribution["advanced"] / total_questions < 0.2:
            gap_analysis["quality_level_gaps"].append("Insufficient advanced analytical questions")
        
        # Gap Analysis 3: Control Coverage
        control_mentions = {}
        for question in all_questions:
            question_text = question["question"].lower()
            if "sox" in question_text:
                if "404" in question_text:
                    control_mentions["SOX_404"] = control_mentions.get("SOX_404", 0) + 1
                if "302" in question_text:
                    control_mentions["SOX_302"] = control_mentions.get("SOX_302", 0) + 1
        
        if control_mentions.get("SOX_404", 0) < 10:
            gap_analysis["control_coverage_gaps"].append("Insufficient SOX 404 control questions")
        if control_mentions.get("SOX_302", 0) < 5:
            gap_analysis["control_coverage_gaps"].append("Insufficient SOX 302 control questions")
        
        # Generate Recommendations
        gap_analysis["recommendations"] = [
            f"Generate {len(missing_evidence)} additional evidence types: {', '.join(missing_evidence)}",
            "Create quality-stratified documents (High/Medium/Low/Fail)",
            "Add specific SOX control ID references to all documents",
            "Include role-based approval workflows in evidence",
            "Add technical validation logs and system timestamps"
        ]
        
        return gap_analysis
    
    def create_quality_stratified_content(self, base_content: Dict[str, Any], 
                                        quality_level: QualityLevel,
                                        document_type: str) -> Dict[str, Any]:
        """Create content variations based on quality level"""
        
        enhanced_content = base_content.copy()
        
        if quality_level == QualityLevel.HIGH:
            # High quality: Comprehensive, detailed, compliant
            enhanced_content = self._enhance_high_quality(enhanced_content, document_type)
            
        elif quality_level == QualityLevel.MEDIUM:
            # Medium quality: Good but some minor gaps (our current level)
            enhanced_content = self._enhance_medium_quality(enhanced_content, document_type)
            
        elif quality_level == QualityLevel.LOW:
            # Low quality: Missing details, incomplete procedures
            enhanced_content = self._enhance_low_quality(enhanced_content, document_type)
            
        elif quality_level == QualityLevel.FAIL:
            # Fail quality: Significant compliance failures
            enhanced_content = self._enhance_fail_quality(enhanced_content, document_type)
        
        return enhanced_content
    
    def _enhance_high_quality(self, content: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Create high-quality evidence with comprehensive compliance"""
        
        if doc_type == "access_review":
            content["executive_summary"] += " All procedures were executed in accordance with SOX 404 requirements with comprehensive documentation and management oversight."
            content["sox_compliance_analysis"] += " The review demonstrates exemplary adherence to internal control frameworks with robust segregation of duties and comprehensive audit trails."
            content["management_response"] += " Management has implemented industry-leading automated controls with real-time monitoring and quarterly effectiveness assessments."
            
        elif doc_type == "financial_reconciliation":
            content["reconciliation_overview"] += " All reconciling items have been thoroughly investigated with complete supporting documentation and management approval within established timeframes."
            content["sox_controls"] += " Advanced automated three-way matching controls are in place with exception reporting and management dashboard monitoring for real-time oversight."
            
        elif doc_type == "risk_assessment":
            content["executive_summary"] += " This comprehensive risk assessment demonstrates mature control design with quantified risk metrics and robust monitoring procedures."
            content["sox_evaluation"] += " Control effectiveness testing shows consistent operation with comprehensive documentation and management oversight exceeding SOX 404 requirements."
        
        return content
    
    def _enhance_medium_quality(self, content: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Create medium-quality evidence (baseline - our current level)"""
        # This is our current quality level - no changes needed
        return content
    
    def _enhance_low_quality(self, content: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Create low-quality evidence with gaps and deficiencies"""
        
        if doc_type == "access_review":
            content["executive_summary"] = content["executive_summary"].replace("comprehensive", "basic").replace("detailed", "limited")
            content["sox_compliance_analysis"] += " However, some documentation gaps were noted and quarterly review procedures need improvement."
            content["management_response"] = "Management acknowledges the findings and will address them in the next quarter."
            
        elif doc_type == "financial_reconciliation":
            content["reconciliation_overview"] = content["reconciliation_overview"].replace("detailed analysis", "review")
            content["sox_controls"] += " Some manual procedures rely on spreadsheet controls with limited automated validation."
            
        elif doc_type == "risk_assessment":
            content["executive_summary"] = content["executive_summary"].replace("comprehensive", "preliminary")
            content["sox_evaluation"] += " Some control testing was limited due to timing constraints and resource availability."
        
        return content
    
    def _enhance_fail_quality(self, content: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """Create failing evidence with significant compliance issues"""
        
        if doc_type == "access_review":
            content["executive_summary"] += " CRITICAL: Multiple segregation of duties violations identified with inadequate management oversight."
            content["sox_compliance_analysis"] = "MATERIAL WEAKNESS: The access review process fails to meet SOX 404 requirements due to inadequate procedures and lack of proper documentation."
            content["management_response"] = "Management is developing a remediation plan but timeline for implementation is uncertain."
            
        elif doc_type == "financial_reconciliation":
            content["reconciliation_overview"] += " EXCEPTION: Significant unreconciled differences exceed materiality thresholds."
            content["sox_controls"] = "DEFICIENCY: Manual reconciliation procedures lack adequate review and approval controls required by SOX 302."
            
        elif doc_type == "risk_assessment":
            content["executive_summary"] += " MATERIAL WEAKNESS: Risk assessment procedures are inadequate and fail to identify key financial reporting risks."
            content["sox_evaluation"] = "ADVERSE OPINION: Control design and operating effectiveness are inadequate to prevent or detect material misstatements."
        
        return content
    
    def add_sox_control_metadata(self, template: Dict[str, Any], 
                                document_type: str) -> Dict[str, Any]:
        """Add specific SOX control IDs and objectives to document template"""
        
        control_mapping = self.sox_control_mappings[document_type]
        
        template["sox_controls_detailed"] = {
            "primary_control_ids": [control.value for control in control_mapping["primary_controls"]],
            "secondary_control_ids": [control.value for control in control_mapping["secondary_controls"]],
            "control_objectives": control_mapping["control_objectives"],
            "control_testing_frequency": "Quarterly",
            "control_owner": "Finance Director",
            "last_assessment_date": "2024-03-31",
            "next_assessment_due": "2024-06-30"
        }
        
        return template
    
    def generate_enhanced_document_set(self, company: CompanyProfile, 
                                     document_type: DocumentType,
                                     quality_level: QualityLevel) -> Dict[str, Any]:
        """Generate enhanced document set with quality stratification and SOX control mapping"""
        
        # Generate base template and content
        if document_type == DocumentType.ACCESS_REVIEW:
            template = self.template_engine.create_access_review_template(company)
        elif document_type == DocumentType.FINANCIAL_RECONCILIATION:
            template = self.template_engine.create_financial_reconciliation_template(company)
        elif document_type == DocumentType.RISK_ASSESSMENT:
            template = self.template_engine.create_risk_assessment_template(company)
        
        # Add SOX control metadata
        template = self.add_sox_control_metadata(template, document_type.value)
        
        # Generate base content
        base_content = self.content_generator.generate_mock_content(document_type, company)
        
        # Apply quality stratification
        enhanced_content = self.create_quality_stratified_content(
            base_content, quality_level, document_type.value
        )
        
        # Create enhanced document data
        document_data = {
            "metadata": {
                "document_type": document_type.value,
                "company": company.value,
                "quality_level": quality_level.value,
                "sox_control_ids": template["sox_controls_detailed"]["primary_control_ids"],
                "generated_at": datetime.now().isoformat(),
                "template_version": "2.0_enhanced",
                "content_type": "ragas_enhanced"
            },
            "template_structure": template,
            "generated_content": enhanced_content
        }
        
        return document_data
    
    def generate_all_quality_levels(self) -> Dict[str, Any]:
        """Generate documents for all companies, document types, and quality levels"""
        
        results = {
            "generation_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_documents": 0,
                "successful_documents": 0,
                "quality_distribution": {quality.value: 0 for quality in QualityLevel},
                "sox_control_coverage": {}
            },
            "documents": {}
        }
        
        # Generate for all combinations
        for company in CompanyProfile:
            for doc_type in DocumentType:
                for quality in QualityLevel:
                    try:
                        doc_data = self.generate_enhanced_document_set(company, doc_type, quality)
                        
                        # Create unique key
                        doc_key = f"{company.value}_{doc_type.value}_{quality.value}"
                        results["documents"][doc_key] = doc_data
                        
                        # Update counters
                        results["generation_summary"]["total_documents"] += 1
                        results["generation_summary"]["successful_documents"] += 1
                        results["generation_summary"]["quality_distribution"][quality.value] += 1
                        
                        # Track SOX control coverage
                        for control_id in doc_data["metadata"]["sox_control_ids"]:
                            if control_id not in results["generation_summary"]["sox_control_coverage"]:
                                results["generation_summary"]["sox_control_coverage"][control_id] = 0
                            results["generation_summary"]["sox_control_coverage"][control_id] += 1
                            
                    except Exception as e:
                        print(f"Error generating {company.value} {doc_type.value} {quality.value}: {str(e)}")
                        results["generation_summary"]["total_documents"] += 1
        
        # Save results
        output_file = self.output_dir / "enhanced_generation_summary.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results

def main():
    """Test the RAGAS-enhanced synthetic data generation"""
    print("🚀 Starting RAGAS-Enhanced Synthetic Data Generation")
    print("=" * 70)
    
    # Initialize enhanced generator
    enhanced_generator = RAGASEnhancedGenerator()
    
    print(f"\n📁 Enhanced output directory: {enhanced_generator.output_dir}")
    
    # Step 1: Analyze existing Q&A dataset for gaps
    print(f"\n🔍 Step 1: RAGAS Gap Analysis...")
    
    qa_dataset_path = "data/qa_datasets/complete_qa_dataset.json"
    if Path(qa_dataset_path).exists():
        gap_analysis = enhanced_generator.analyze_qa_gaps(qa_dataset_path)
        
        print(f"✅ Gap analysis completed!")
        print(f"   Missing Evidence Types: {len(gap_analysis['missing_evidence_types'])}")
        print(f"   Quality Level Gaps: {len(gap_analysis['quality_level_gaps'])}")
        print(f"   Control Coverage Gaps: {len(gap_analysis['control_coverage_gaps'])}")
        print(f"   Recommendations: {len(gap_analysis['recommendations'])}")
        
        # Save gap analysis
        gap_file = enhanced_generator.output_dir / "ragas_gap_analysis.json"
        with open(gap_file, 'w', encoding='utf-8') as f:
            json.dump(gap_analysis, f, indent=2)
        
    else:
        print(f"⚠️  Q&A dataset not found at {qa_dataset_path}")
        print(f"   Proceeding with enhancement based on best practices...")
    
    # Step 2: Generate test document with quality stratification
    print(f"\n🧪 Step 2: Testing Quality Stratification...")
    
    test_docs = {}
    for quality in QualityLevel:
        doc_data = enhanced_generator.generate_enhanced_document_set(
            CompanyProfile.UBER, 
            DocumentType.ACCESS_REVIEW, 
            quality
        )
        test_docs[quality.value] = doc_data
        print(f"   ✅ {quality.value.title()} quality document generated")
    
    # Step 3: Generate all enhanced documents
    print(f"\n🚀 Step 3: Generating All Enhanced Documents...")
    print(f"   Target: {len(CompanyProfile)} companies × {len(DocumentType)} doc types × {len(QualityLevel)} quality levels")
    print(f"   Total: {len(CompanyProfile) * len(DocumentType) * len(QualityLevel)} documents")
    
    results = enhanced_generator.generate_all_quality_levels()
    
    summary = results["generation_summary"]
    print(f"\n📊 Enhanced Generation Complete!")
    print(f"   Total Documents: {summary['total_documents']}")
    print(f"   Successful: {summary['successful_documents']}")
    print(f"   Success Rate: {(summary['successful_documents']/summary['total_documents'])*100:.1f}%")
    print(f"   Quality Distribution:")
    for quality, count in summary['quality_distribution'].items():
        print(f"     - {quality.title()}: {count} documents")
    print(f"   SOX Control Coverage: {len(summary['sox_control_coverage'])} unique controls")
    
    print(f"\n🎯 RAGAS-Enhanced generation completed successfully!")
    print(f"⚡ Quality-stratified documents ready for robust RAG testing")
    print(f"📂 Enhanced files saved to: {enhanced_generator.output_dir}")
    
    return results

if __name__ == "__main__":
    results = main() 