"""
Synthetic Data Generation for Verityn AI
Task 3: Subtask 3.1 - Document Template Design

This module creates realistic audit document templates for:
- Access Reviews (SOX 404)
- Financial Reconciliations (SOX 302) 
- Risk Assessments (SOX 404)

Focused on enterprise companies like Uber, Walmart with medium complexity (7/10)
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class DocumentType(Enum):
    ACCESS_REVIEW = "access_review"
    FINANCIAL_RECONCILIATION = "financial_reconciliation"
    RISK_ASSESSMENT = "risk_assessment"

class CompanyProfile(Enum):
    UBER = "uber"
    WALMART = "walmart" 
    AMAZON = "amazon"

@dataclass
class EnterpriseContext:
    """Enterprise-specific context for realistic document generation"""
    name: str
    business_model: str
    industry: str
    key_systems: List[str]
    departments: List[str]
    common_risks: List[str]
    typical_controls: List[str]
    financial_scale: str

class DocumentTemplateEngine:
    """Handles creation of realistic document templates for enterprise audit documents"""
    
    def __init__(self):
        self.enterprise_contexts = self._initialize_enterprise_contexts()
        self.sox_controls = self._initialize_sox_controls()
        
    def _initialize_enterprise_contexts(self) -> Dict[CompanyProfile, EnterpriseContext]:
        """Initialize enterprise-specific contexts for realistic document generation"""
        return {
            CompanyProfile.UBER: EnterpriseContext(
                name="Uber Technologies Inc.",
                business_model="Global ride-sharing and delivery platform",
                industry="Transportation Technology",
                key_systems=[
                    "Driver Payment Platform",
                    "Rider Billing System", 
                    "Financial Reporting System",
                    "Regulatory Compliance Portal"
                ],
                departments=[
                    "Driver Operations",
                    "Finance & Accounting", 
                    "Risk Management",
                    "Legal & Compliance",
                    "Product Engineering",
                    "Business Intelligence"
                ],
                common_risks=[
                    "Driver payment processing errors",
                    "Revenue recognition complexity",
                    "Multi-currency transaction risks",
                    "Regulatory compliance across jurisdictions",
                    "Real-time transaction volume spikes"
                ],
                typical_controls=[
                    "Automated payment reconciliation",
                    "Multi-level approval workflows",
                    "Real-time fraud monitoring",
                    "Segregation of payment duties"
                ],
                financial_scale="$31B annual revenue"
            ),
            
            CompanyProfile.WALMART: EnterpriseContext(
                name="Walmart Inc.",
                business_model="Global retail and e-commerce operations",
                industry="Retail",
                key_systems=[
                    "Point of Sale Systems",
                    "Supply Chain Management",
                    "Vendor Payment Portal",
                    "Inventory Management System"
                ],
                departments=[
                    "Merchandising",
                    "Supply Chain",
                    "Finance & Accounting",
                    "Store Operations", 
                    "E-commerce",
                    "Internal Audit"
                ],
                common_risks=[
                    "Inventory valuation accuracy",
                    "Vendor payment processing",
                    "Sales recognition timing",
                    "Supply chain disruptions",
                    "Multi-location operational risks"
                ],
                typical_controls=[
                    "Cycle count procedures",
                    "Three-way purchase matching",
                    "Daily sales reconciliation",
                    "Vendor master data controls"
                ],
                financial_scale="$611B annual revenue"
            ),
            
            CompanyProfile.AMAZON: EnterpriseContext(
                name="Amazon.com Inc.",
                business_model="E-commerce, cloud services, and digital platforms",
                industry="Technology/Retail",
                key_systems=[
                    "AWS Financial Management",
                    "Marketplace Payment System",
                    "Supply Chain Optimization",
                    "Customer Account Management"
                ],
                departments=[
                    "AWS Finance",
                    "Retail Operations",
                    "Finance & Accounting",
                    "Risk Management",
                    "Seller Services",
                    "Customer Experience"
                ],
                common_risks=[
                    "Third-party seller payment accuracy",
                    "AWS usage revenue recognition", 
                    "Inventory obsolescence",
                    "Customer refund processing",
                    "International tax compliance"
                ],
                typical_controls=[
                    "Automated seller payment reconciliation",
                    "Usage-based billing controls",
                    "Customer refund approval limits",
                    "Multi-currency hedging procedures"
                ],
                financial_scale="$574B annual revenue"
            )
        }
    
    def _initialize_sox_controls(self) -> Dict[str, Dict]:
        """Initialize SOX control frameworks and references"""
        return {
            "section_302": {
                "title": "Corporate Responsibility for Financial Reports",
                "key_controls": [
                    "Management assessment of disclosure controls",
                    "Quarterly certification procedures",
                    "Material change evaluation",
                    "Financial reporting accuracy"
                ]
            },
            "section_404": {
                "title": "Assessment of Internal Control",
                "key_controls": [
                    "Internal control over financial reporting (ICFR)",
                    "Management assessment procedures",
                    "External auditor attestation",
                    "Control deficiency remediation"
                ]
            }
        }
    
    def create_access_review_template(self, company: CompanyProfile) -> Dict[str, Any]:
        """Create realistic access review template for enterprise company"""
        context = self.enterprise_contexts[company]
        
        template = {
            "document_type": DocumentType.ACCESS_REVIEW.value,
            "sox_section": "404",
            "company_context": {
                "name": context.name,
                "business_model": context.business_model,
                "industry": context.industry,
                "financial_scale": context.financial_scale
            },
            "document_structure": {
                "header": {
                    "title": "Quarterly User Access Review Report",
                    "period": "Q1 2024",
                    "review_date": "2024-03-31",
                    "reviewer": "SOX Compliance Team",
                    "approver": "Chief Financial Officer"
                },
                "executive_summary": {
                    "total_users_reviewed": random.randint(280, 420),
                    "systems_covered": len(context.key_systems),
                    "high_risk_findings": random.randint(2, 5),
                    "medium_risk_findings": random.randint(8, 15),
                    "low_risk_findings": random.randint(5, 12),
                    "control_effectiveness": random.choice([
                        "Effective with minor deficiencies",
                        "Needs improvement", 
                        "Generally effective"
                    ])
                },
                "systems_reviewed": context.key_systems,
                "departments_covered": context.departments,
                "user_access_analysis": {
                    "privileged_users": random.randint(25, 45),
                    "terminated_users_found": random.randint(1, 3),
                    "excessive_access": random.randint(3, 8),
                    "segregation_violations": random.randint(1, 4)
                },
                "sox_findings": {
                    "control_gaps": [
                        "Segregation of duties violations in payment processing",
                        "Terminated user access not promptly removed",
                        "Excessive administrative privileges granted"
                    ],
                    "management_response": [
                        "Implement automated access removal process",
                        "Enhanced quarterly access reviews",
                        "Privilege escalation approval workflow"
                    ]
                }
            },
            "data_tables": {
                "user_access_table": {
                    "columns": [
                        "UserID", "Employee_Name", "Department", "Job_Title",
                        "System_Access", "Access_Level", "Last_Login", 
                        "SOX_Critical", "Review_Status", "Findings"
                    ],
                    "estimated_rows": random.randint(280, 420)
                },
                "findings_summary": {
                    "columns": [
                        "Finding_ID", "System", "User", "Issue_Type", 
                        "Risk_Level", "SOX_Impact", "Remediation", "Due_Date"
                    ],
                    "estimated_rows": random.randint(15, 25)
                }
            }
        }
        
        return template
    
    def create_financial_reconciliation_template(self, company: CompanyProfile) -> Dict[str, Any]:
        """Create realistic financial reconciliation template for enterprise company"""
        context = self.enterprise_contexts[company]
        
        # Generate realistic financial amounts based on company scale
        if "31B" in context.financial_scale:  # Uber scale
            base_amount = random.randint(15_000_000, 35_000_000)
        elif "611B" in context.financial_scale:  # Walmart scale  
            base_amount = random.randint(45_000_000, 85_000_000)
        else:  # Amazon scale
            base_amount = random.randint(65_000_000, 120_000_000)
        
        difference = random.randint(5_000, 50_000) * random.choice([1, -1])
        
        template = {
            "document_type": DocumentType.FINANCIAL_RECONCILIATION.value,
            "sox_section": "302",
            "company_context": {
                "name": context.name,
                "business_model": context.business_model,
                "industry": context.industry
            },
            "document_structure": {
                "header": {
                    "title": "Monthly Bank Reconciliation",
                    "account_name": "Operating Cash Account - Primary",
                    "account_number": f"****{random.randint(1000, 9999)}",
                    "period": "March 2024",
                    "preparer": "Senior Staff Accountant",
                    "reviewer": "Accounting Manager",
                    "approver": "Assistant Controller"
                },
                "reconciliation_summary": {
                    "book_balance": base_amount,
                    "bank_balance": base_amount + difference,
                    "total_adjustments": abs(difference),
                    "reconciled_balance": base_amount,
                    "variance_threshold": "$10,000",
                    "variance_explanation_required": abs(difference) > 10000
                },
                "reconciling_items": {
                    "deposits_in_transit": random.randint(8, 15),
                    "outstanding_checks": random.randint(25, 45),
                    "bank_fees": random.randint(3, 7),
                    "interest_earned": random.randint(1, 3),
                    "nsf_charges": random.randint(0, 2),
                    "wire_transfers": random.randint(2, 8)
                },
                "sox_controls": {
                    "three_way_match": "Completed and documented",
                    "management_review": "Approved by Assistant Controller",
                    "supporting_documentation": "Bank statements and transaction details attached",
                    "approval_signatures": "Electronic signatures captured",
                    "exception_handling": "All variances >$10K investigated and documented"
                }
            },
            "data_tables": {
                "reconciling_items_detail": {
                    "columns": [
                        "Date", "Description", "Reference_Number", "Amount",
                        "Type", "Status", "SOX_Control_Point", "Reviewer"
                    ],
                    "estimated_rows": random.randint(60, 100)
                },
                "outstanding_items": {
                    "columns": [
                        "Check_Number", "Date_Issued", "Payee", "Amount",
                        "Days_Outstanding", "Follow_up_Required", "Status"
                    ],
                    "estimated_rows": random.randint(25, 45)
                }
            }
        }
        
        return template
    
    def create_risk_assessment_template(self, company: CompanyProfile) -> Dict[str, Any]:
        """Create realistic risk assessment template for enterprise company"""
        context = self.enterprise_contexts[company]
        
        # Select a major financial process for assessment
        financial_processes = [
            "Revenue Recognition Process",
            "Procurement and Accounts Payable", 
            "Financial Close and Reporting",
            "Cash Management and Treasury"
        ]
        
        selected_process = random.choice(financial_processes)
        
        template = {
            "document_type": DocumentType.RISK_ASSESSMENT.value,
            "sox_section": "404",
            "company_context": {
                "name": context.name,
                "business_model": context.business_model,
                "industry": context.industry
            },
            "document_structure": {
                "header": {
                    "title": f"SOX 404 Risk Assessment - {selected_process}",
                    "assessment_period": "Q1 2024",
                    "assessment_date": "2024-03-31",
                    "lead_assessor": "Internal Audit Manager",
                    "process_owner": "Finance Director",
                    "risk_committee_review": "2024-04-15"
                },
                "process_overview": {
                    "process_name": selected_process,
                    "business_impact": "High - Direct impact on financial reporting accuracy",
                    "annual_volume": f"${random.randint(500, 2000)}M in transactions",
                    "key_systems": random.sample(context.key_systems, 2),
                    "involved_departments": random.sample(context.departments, 3)
                },
                "risk_summary": {
                    "total_risks_identified": random.randint(18, 28),
                    "high_risks": random.randint(3, 6),
                    "medium_risks": random.randint(8, 15),
                    "low_risks": random.randint(5, 10),
                    "inherent_risk_rating": random.choice(["High", "Medium-High"]),
                    "residual_risk_rating": random.choice(["Medium", "Medium-Low"])
                },
                "key_risks": [
                    {
                        "risk_id": "R001",
                        "description": f"Inaccurate {selected_process.lower()} due to system errors",
                        "likelihood": random.choice(["Low", "Medium", "High"]),
                        "impact": random.choice(["Medium", "High"]),
                        "risk_rating": random.choice(["Medium", "High"]),
                        "control_description": "Automated system controls and manual reviews"
                    },
                    {
                        "risk_id": "R002", 
                        "description": "Unauthorized changes to financial data",
                        "likelihood": random.choice(["Low", "Medium"]),
                        "impact": "High",
                        "risk_rating": random.choice(["Medium", "High"]),
                        "control_description": "Role-based access controls and approval workflows"
                    }
                ],
                "sox_assessment": {
                    "control_design_effectiveness": random.choice([
                        "Effective", 
                        "Effective with minor gaps",
                        "Needs improvement"
                    ]),
                    "operating_effectiveness": random.choice([
                        "Effective",
                        "Generally effective with exceptions",
                        "Deficiencies noted"
                    ]),
                    "management_response": "Action plan developed for identified deficiencies",
                    "remediation_timeline": "60-90 days for high priority items"
                }
            },
            "data_tables": {
                "risk_register": {
                    "columns": [
                        "Risk_ID", "Risk_Description", "Process_Step", "Likelihood", 
                        "Impact", "Risk_Rating", "Control_Description", "Control_Owner",
                        "Testing_Frequency", "Last_Test_Date", "Test_Results", "Action_Required"
                    ],
                    "estimated_rows": random.randint(18, 28)
                },
                "control_matrix": {
                    "columns": [
                        "Control_ID", "Control_Description", "Control_Type", "Frequency",
                        "Owner", "SOX_Relevant", "Design_Effective", "Operating_Effective",
                        "Deficiencies", "Management_Response"
                    ],
                    "estimated_rows": random.randint(15, 25)
                }
            }
        }
        
        return template
    
    def generate_csv_data(self, template: Dict[str, Any], num_rows: int = None) -> Dict[str, List[Dict]]:
        """Generate realistic CSV data based on template data tables"""
        csv_data = {}
        
        for table_name, table_config in template["data_tables"].items():
            if num_rows is None:
                rows_to_generate = table_config["estimated_rows"]
            else:
                rows_to_generate = min(num_rows, table_config["estimated_rows"])
            
            # Generate sample data for each table
            if "user_access" in table_name:
                csv_data[table_name] = self._generate_user_access_data(
                    table_config["columns"], rows_to_generate
                )
            elif "reconciling_items" in table_name:
                csv_data[table_name] = self._generate_reconciliation_data(
                    table_config["columns"], rows_to_generate
                )
            elif "risk_register" in table_name:
                csv_data[table_name] = self._generate_risk_data(
                    table_config["columns"], rows_to_generate
                )
            else:
                # Generic data generation
                csv_data[table_name] = self._generate_generic_data(
                    table_config["columns"], rows_to_generate
                )
        
        return csv_data
    
    def _generate_user_access_data(self, columns: List[str], num_rows: int) -> List[Dict]:
        """Generate realistic user access data"""
        departments = ["Finance", "Accounting", "Treasury", "Operations", "IT", "Legal"]
        job_titles = ["Analyst", "Senior Analyst", "Manager", "Director", "VP"]
        access_levels = ["Read Only", "Standard User", "Power User", "Administrator"]
        
        data = []
        for i in range(num_rows):
            row = {}
            for col in columns:
                if col == "UserID":
                    row[col] = f"U{1000 + i:04d}"
                elif col == "Employee_Name":
                    row[col] = f"Employee_{i+1:03d}"
                elif col == "Department":
                    row[col] = random.choice(departments)
                elif col == "Job_Title":
                    row[col] = random.choice(job_titles)
                elif col == "Access_Level":
                    row[col] = random.choice(access_levels)
                elif col == "SOX_Critical":
                    row[col] = random.choice(["Yes", "No"])
                elif col == "Review_Status":
                    row[col] = random.choice(["Approved", "Pending", "Exception"])
                else:
                    row[col] = f"Data_{i+1}"
            data.append(row)
        
        return data
    
    def _generate_reconciliation_data(self, columns: List[str], num_rows: int) -> List[Dict]:
        """Generate realistic reconciliation data"""
        data = []
        for i in range(num_rows):
            row = {}
            for col in columns:
                if col == "Date":
                    row[col] = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
                elif col == "Amount":
                    row[col] = f"${random.randint(100, 50000):,}"
                elif col == "Type":
                    row[col] = random.choice(["Deposit", "Check", "Wire", "Fee", "Interest"])
                elif col == "Status":
                    row[col] = random.choice(["Cleared", "Outstanding", "Reconciled"])
                else:
                    row[col] = f"Item_{i+1:03d}"
            data.append(row)
        
        return data
    
    def _generate_risk_data(self, columns: List[str], num_rows: int) -> List[Dict]:
        """Generate realistic risk assessment data"""
        data = []
        for i in range(num_rows):
            row = {}
            for col in columns:
                if col == "Risk_ID":
                    row[col] = f"R{i+1:03d}"
                elif col == "Likelihood":
                    row[col] = random.choice(["Low", "Medium", "High"])
                elif col == "Impact":
                    row[col] = random.choice(["Low", "Medium", "High"])
                elif col == "Risk_Rating":
                    row[col] = random.choice(["Low", "Medium", "High", "Critical"])
                elif col == "SOX_Relevant":
                    row[col] = random.choice(["Yes", "No"])
                else:
                    row[col] = f"Risk_Item_{i+1}"
            data.append(row)
        
        return data
    
    def _generate_generic_data(self, columns: List[str], num_rows: int) -> List[Dict]:
        """Generate generic data for any table structure"""
        data = []
        for i in range(num_rows):
            row = {col: f"{col}_{i+1}" for col in columns}
            data.append(row)
        
        return data
    
    def generate_all_templates(self) -> Dict[str, Any]:
        """Generate all document templates for all companies"""
        all_templates = {}
        
        for company in CompanyProfile:
            company_templates = {
                "access_review": self.create_access_review_template(company),
                "financial_reconciliation": self.create_financial_reconciliation_template(company),
                "risk_assessment": self.create_risk_assessment_template(company)
            }
            all_templates[company.value] = company_templates
            
        return all_templates

def main():
    """Test the document template generation"""
    print("🏗️ Starting Subtask 3.1: Document Template Design")
    print("=" * 60)
    
    # Initialize template engine
    template_engine = DocumentTemplateEngine()
    
    # Generate templates for one company as test
    print("\n📋 Generating test templates for Uber...")
    uber_templates = {
        "access_review": template_engine.create_access_review_template(CompanyProfile.UBER),
        "financial_reconciliation": template_engine.create_financial_reconciliation_template(CompanyProfile.UBER),
        "risk_assessment": template_engine.create_risk_assessment_template(CompanyProfile.UBER)
    }
    
    # Display template summaries
    for doc_type, template in uber_templates.items():
        print(f"\n✅ {doc_type.replace('_', ' ').title()} Template:")
        print(f"   Company: {template['company_context']['name']}")
        print(f"   SOX Section: {template['sox_section']}")
        print(f"   Structure Keys: {list(template['document_structure'].keys())}")
        print(f"   Data Tables: {list(template['data_tables'].keys())}")
    
    print(f"\n🎯 Template generation completed successfully!")
    print(f"📊 Each template includes:")
    print(f"   - Enterprise-specific context")
    print(f"   - Realistic business data ranges")
    print(f"   - SOX compliance elements")
    print(f"   - Professional document structure")
    print(f"   - Data tables for CSV export")
    
    return uber_templates

if __name__ == "__main__":
    templates = main() 