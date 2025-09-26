"""
Specialized SOX Compliance Document Generator for Verityn AI

This script creates realistic SOX compliance documents for audit test scenarios:
1. SOX Access Review Report
2. SOX Risk Assessment Document  
3. SOX Financial Controls Assessment
4. SOX Internal Controls Evaluation

Generates comprehensive test data for web search functionality and compliance analysis.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class SOXDocumentGenerator:
    """Generates realistic SOX compliance documents for testing"""
    
    def __init__(self, output_dir: str = "data/sox_test_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "pdf").mkdir(exist_ok=True)
        (self.output_dir / "json").mkdir(exist_ok=True)
        
    def generate_sox_access_review(self) -> Dict[str, Any]:
        """Generate SOX 404 Access Review Report"""
        return {
            "metadata": {
                "document_type": "SOX Access Review Report",
                "framework": "SOX 404",
                "company": "TechCorp Solutions Inc.",
                "period": "Q4 2024",
                "review_date": "2024-12-15",
                "reviewer": "Sarah Johnson, Senior Auditor",
                "approver": "Michael Chen, Audit Director"
            },
            "content": {
                "executive_summary": "This access review evaluates user access controls across critical financial systems to ensure compliance with SOX 404 requirements for the quarter ending December 31, 2024.",
                "scope": "Review covers ERP system, financial reporting platform, and treasury management system access for Q4 2024.",
                "key_findings": [
                    "3 users identified with excessive privileges requiring immediate remediation",
                    "2 orphaned accounts found and disabled",
                    "Access review process needs enhancement for quarterly reviews",
                    "Segregation of duties matrix updated for 2025"
                ],
                "risk_assessment": "Medium risk level due to excessive privileges and process gaps",
                "recommendations": [
                    "Implement role-based access controls (RBAC) by Q1 2025",
                    "Establish quarterly access review process",
                    "Enhance monitoring for privileged user activities",
                    "Update access request and approval workflows"
                ],
                "compliance_status": "Partially compliant - requires remediation by Q1 2025"
            }
        }
    
    def generate_sox_risk_assessment(self) -> Dict[str, Any]:
        """Generate SOX 404 Risk Assessment Document"""
        return {
            "metadata": {
                "document_type": "SOX Risk Assessment",
                "framework": "SOX 404",
                "company": "Global Manufacturing Corp",
                "period": "Annual 2024",
                "assessment_date": "2024-12-01",
                "assessor": "David Rodriguez, Risk Manager",
                "approver": "Lisa Thompson, CFO"
            },
            "content": {
                "executive_summary": "Annual risk assessment of internal controls over financial reporting as required by SOX 404, identifying key risks and control effectiveness.",
                "risk_categories": {
                    "financial_reporting": "High",
                    "access_controls": "Medium",
                    "change_management": "Low",
                    "vendor_management": "Medium"
                },
                "key_risks": [
                    "Revenue recognition complexity in multi-currency operations",
                    "IT system access controls and segregation of duties",
                    "Third-party vendor access to financial systems",
                    "Change management controls for system modifications"
                ],
                "control_effectiveness": {
                    "effective": ["Financial reporting controls", "Audit trail monitoring"],
                    "needs_improvement": ["Access controls", "Vendor management"],
                    "ineffective": ["Change management controls"]
                },
                "material_weaknesses": [
                    "Inadequate change management controls for financial systems",
                    "Weak vendor access controls and monitoring"
                ],
                "remediation_plan": "Implement enhanced change management and vendor controls by Q2 2025"
            }
        }
    
    def generate_sox_financial_controls(self) -> Dict[str, Any]:
        """Generate SOX Financial Controls Assessment"""
        return {
            "metadata": {
                "document_type": "SOX Financial Controls Assessment",
                "framework": "SOX 302",
                "company": "Innovation Tech Solutions",
                "period": "Q4 2024",
                "assessment_date": "2024-12-20",
                "assessor": "Jennifer Lee, Financial Controller",
                "approver": "Robert Kim, CEO"
            },
            "content": {
                "executive_summary": "Assessment of disclosure controls and procedures for financial reporting as required by SOX 302, ensuring accuracy and completeness of financial statements.",
                "control_objectives": [
                    "Ensure accurate financial reporting",
                    "Maintain effective internal controls",
                    "Provide timely disclosure of material changes",
                    "Establish accountability for financial reporting"
                ],
                "control_activities": {
                    "revenue_recognition": "Automated controls with manual review",
                    "expense_processing": "Multi-level approval workflow",
                    "financial_close": "Standardized closing procedures",
                    "disclosure_controls": "Legal and finance review process"
                },
                "testing_results": {
                    "revenue_controls": "Effective - 95% compliance",
                    "expense_controls": "Effective - 92% compliance",
                    "close_procedures": "Needs improvement - 78% compliance",
                    "disclosure_controls": "Effective - 88% compliance"
                },
                "deficiencies": [
                    "Financial close procedures need standardization",
                    "Documentation of control activities incomplete"
                ],
                "remediation_status": "In progress - target completion Q1 2025"
            }
        }
    
    def generate_sox_internal_controls(self) -> Dict[str, Any]:
        """Generate SOX Internal Controls Evaluation"""
        return {
            "metadata": {
                "document_type": "SOX Internal Controls Evaluation",
                "framework": "SOX 404",
                "company": "Healthcare Systems International",
                "period": "Q4 2024",
                "evaluation_date": "2024-12-10",
                "evaluator": "Thomas Wilson, Internal Audit Manager",
                "approver": "Maria Garcia, Audit Committee Chair"
            },
            "content": {
                "executive_summary": "Comprehensive evaluation of internal controls over financial reporting, identifying control strengths and areas requiring improvement.",
                "control_environment": {
                    "tone_at_top": "Strong commitment to integrity and ethical values",
                    "organizational_structure": "Clear reporting lines and accountability",
                    "human_resources": "Competent personnel with appropriate training",
                    "risk_assessment": "Systematic process for identifying and analyzing risks"
                },
                "control_activities": {
                    "authorization": "Proper approval procedures in place",
                    "segregation": "Duties adequately separated",
                    "documentation": "Controls properly documented",
                    "monitoring": "Ongoing monitoring activities established"
                },
                "information_systems": {
                    "general_controls": "Effective IT general controls",
                    "application_controls": "Most application controls effective",
                    "data_integrity": "Strong data validation controls",
                    "security": "Comprehensive security measures"
                },
                "monitoring_activities": {
                    "ongoing_monitoring": "Real-time monitoring of key controls",
                    "separate_evaluations": "Regular internal audit reviews",
                    "deficiency_communication": "Effective communication to management"
                },
                "conclusion": "Internal controls are effective with minor deficiencies that do not rise to material weakness level"
            }
        }
    
    def create_json_documents(self):
        """Create JSON versions of all SOX documents"""
        documents = [
            ("sox_access_review_2024", self.generate_sox_access_review()),
            ("sox_risk_assessment_2024", self.generate_sox_risk_assessment()),
            ("sox_financial_controls_2024", self.generate_sox_financial_controls()),
            ("sox_internal_controls_2024", self.generate_sox_internal_controls())
        ]
        
        for filename, content in documents:
            json_path = self.output_dir / "json" / f"{filename}.json"
            with open(json_path, 'w') as f:
                json.dump(content, f, indent=2)
            print(f"✅ Created: {json_path}")
    
    def create_simple_text_documents(self):
        """Create simple text versions for easy testing"""
        documents = [
            ("sox_access_review_2024", self.generate_sox_access_review()),
            ("sox_risk_assessment_2024", self.generate_sox_risk_assessment()),
            ("sox_financial_controls_2024", self.generate_sox_financial_controls()),
            ("sox_internal_controls_2024", self.generate_sox_internal_controls())
        ]
        
        for filename, content in documents:
            txt_path = self.output_dir / f"{filename}.txt"
            
            with open(txt_path, 'w') as f:
                # Write metadata
                f.write(f"Document Type: {content['metadata']['document_type']}\n")
                f.write(f"Framework: {content['metadata']['framework']}\n")
                f.write(f"Company: {content['metadata']['company']}\n")
                f.write(f"Period: {content['metadata']['period']}\n")
                f.write(f"Date: {content['metadata'].get('review_date', content['metadata'].get('assessment_date', content['metadata'].get('evaluation_date', 'N/A')))}\n")
                f.write(f"Prepared By: {content['metadata'].get('reviewer', content['metadata'].get('assessor', content['metadata'].get('evaluator', 'N/A')))}\n")
                f.write(f"Approved By: {content['metadata'].get('approver', 'N/A')}\n")
                f.write("\n" + "="*80 + "\n\n")
                
                # Write content
                for section, section_content in content['content'].items():
                    f.write(f"{section.replace('_', ' ').title()}:\n")
                    if isinstance(section_content, list):
                        for item in section_content:
                            f.write(f"• {item}\n")
                    elif isinstance(section_content, dict):
                        for key, value in section_content.items():
                            f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                    else:
                        f.write(f"{section_content}\n")
                    f.write("\n")
            
            print(f"✅ Created: {txt_path}")
    
    def generate_all_documents(self):
        """Generate all SOX documents in multiple formats"""
        print("🚀 Generating SOX Test Documents for Verityn AI...")
        print("=" * 60)
        
        # Create JSON documents
        print("\n📄 Creating JSON documents...")
        self.create_json_documents()
        
        # Create text documents
        print("\n📝 Creating text documents...")
        self.create_simple_text_documents()
        
        print("\n" + "=" * 60)
        print("🎉 All SOX test documents generated successfully!")
        print(f"📁 Output directory: {self.output_dir}")
        print("\n📋 Generated Documents:")
        print("1. SOX Access Review Report (SOX 404)")
        print("2. SOX Risk Assessment (SOX 404)")
        print("3. SOX Financial Controls Assessment (SOX 302)")
        print("4. SOX Internal Controls Evaluation (SOX 404)")
        print("\n💡 Use these documents to test:")
        print("• Document upload and analysis")
        print("• Web search functionality")
        print("• Compliance framework detection")
        print("• Risk assessment capabilities")

if __name__ == "__main__":
    generator = SOXDocumentGenerator()
    generator.generate_all_documents()
