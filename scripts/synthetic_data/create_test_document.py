#!/usr/bin/env python3
"""
Simple Test Document Creator for Verityn AI

Generates basic SOX Access Review PDFs for quick testing and validation.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def create_test_audit_document():
    """Create a sample SOX Access Review document for testing"""
    
    # Create output directory if it doesn't exist
    os.makedirs('test_documents', exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        "test_documents/SOX_Access_Review_2024.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Story to hold all elements
    story = []
    
    # Title
    title = Paragraph("SOX 404 Access Control Review Report", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    summary_text = """
    This access control review was conducted to assess the effectiveness of user access controls 
    in compliance with SOX 404 requirements. The review covered critical financial systems including 
    the General Ledger, Accounts Payable, and Accounts Receivable modules. The assessment identified 
    several areas requiring immediate attention to ensure proper segregation of duties and access 
    control effectiveness.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Key Findings
    story.append(Paragraph("Key Findings", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    findings_data = [
        ['Finding', 'Risk Level', 'Impact'],
        ['Inactive user accounts not removed within 90 days', 'High', 'Potential unauthorized access'],
        ['Segregation of duties violation in AP module', 'Medium', 'Financial reporting risk'],
        ['Missing approval workflow for system access', 'Medium', 'Control effectiveness'],
        ['Inadequate logging of access changes', 'Low', 'Audit trail completeness']
    ]
    
    findings_table = Table(findings_data, colWidths=[3*inch, 1.5*inch, 2*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 12))
    
    # Detailed Analysis
    story.append(Paragraph("Detailed Analysis", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    analysis_text = """
    <b>User Access Management:</b> The review identified 15 inactive user accounts that have not been 
    removed within the required 90-day timeframe. These accounts represent a potential security risk 
    as they could be exploited for unauthorized access to financial systems.
    
    <b>Segregation of Duties:</b> In the Accounts Payable module, we identified one user with both 
    vendor creation and payment approval privileges, which violates segregation of duties requirements. 
    This creates a risk of fraudulent payments being processed without proper oversight.
    
    <b>Access Approval Process:</b> The current system access approval process lacks formal documentation 
    and approval workflows. Managers are approving access requests via email without proper tracking 
    or verification of business justification.
    
    <b>Audit Logging:</b> While the system maintains basic access logs, the logging is not comprehensive 
    enough to support detailed audit trails. Critical access changes are not being logged with sufficient 
    detail for compliance purposes.
    """
    story.append(Paragraph(analysis_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    recommendations_data = [
        ['Priority', 'Recommendation', 'Timeline'],
        ['High', 'Remove all inactive user accounts within 30 days', 'Immediate'],
        ['High', 'Implement formal access approval workflow', '30 days'],
        ['Medium', 'Review and update segregation of duties matrix', '60 days'],
        ['Medium', 'Enhance audit logging capabilities', '90 days'],
        ['Low', 'Implement quarterly access reviews', 'Ongoing']
    ]
    
    rec_table = Table(recommendations_data, colWidths=[1*inch, 3.5*inch, 1.5*inch])
    rec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 12))
    
    # Compliance Assessment
    story.append(Paragraph("SOX 404 Compliance Assessment", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    compliance_text = """
    Based on the findings of this access control review, the organization's current access control 
    environment requires improvement to fully comply with SOX 404 requirements. The identified 
    deficiencies in user access management and segregation of duties represent material weaknesses 
    that could impact the reliability of financial reporting.
    
    <b>Overall Assessment:</b> The access control environment is rated as "Needs Improvement" with 
    a risk level of "Medium" due to the identified control deficiencies.
    """
    story.append(Paragraph(compliance_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    print("✅ Test document created: test_documents/SOX_Access_Review_2024.pdf")

if __name__ == "__main__":
    create_test_audit_document() 