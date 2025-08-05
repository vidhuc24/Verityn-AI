#!/usr/bin/env python3
"""
Create Verityn AI Application Flowchart
Generates a comprehensive flowchart showing the multi-agent workflow and system architecture.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Set up the figure with high resolution
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# Color scheme
colors = {
    'user': '#E3F2FD',      # Light blue
    'frontend': '#F3E5F5',  # Light purple
    'backend': '#E8F5E8',   # Light green
    'agent': '#FFF3E0',     # Light orange
    'database': '#FCE4EC',  # Light pink
    'external': '#F1F8E9',  # Light lime
    'decision': '#E0F2F1',  # Light teal
    'output': '#F9FBE7'     # Light yellow
}

# Helper function to create rounded rectangles
def create_box(x, y, width, height, text, color, fontsize=9):
    box = FancyBboxPatch((x, y), width, height,
                        boxstyle="round,pad=0.1",
                        facecolor=color,
                        edgecolor='black',
                        linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center', fontsize=fontsize, fontweight='bold',
            wrap=True)

# Helper function to create arrows
def create_arrow(start_x, start_y, end_x, end_y, label=None, style='->'):
    arrow = ConnectionPatch((start_x, start_y), (end_x, end_y), 
                           "data", "data",
                           arrowstyle=style, shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc='black', ec='black',
                           linewidth=2)
    ax.add_patch(arrow)
    if label:
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        ax.text(mid_x, mid_y, label, ha='center', va='center', 
                fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

# Title
ax.text(8, 11.5, 'VERITYN AI - MULTI-AGENT DOCUMENT CHAT SYSTEM', 
        ha='center', va='center', fontsize=16, fontweight='bold')

# User Interface Layer
create_box(0.5, 10.5, 3, 1, 'User\n(Auditor)', colors['user'], 10)
create_box(4, 10.5, 8, 1, 'Next.js Frontend\n(Document Upload, Chat Interface, Smart Questions)', colors['frontend'], 9)
create_box(13, 10.5, 2.5, 1, 'Tavily API\n(Regulatory Guidance)', colors['external'], 9)

# Backend API Layer
create_box(4, 9, 8, 1, 'FastAPI Backend\n(Multi-Agent Orchestration)', colors['backend'], 9)

# Multi-Agent Workflow Layer
create_box(0.5, 7.5, 2.5, 1, 'Document\nProcessing\nAgent', colors['agent'], 8)
create_box(3.5, 7.5, 2.5, 1, 'Classification\nAgent', colors['agent'], 8)
create_box(6.5, 7.5, 2.5, 1, 'Question\nAnalysis\nAgent', colors['agent'], 8)
create_box(9.5, 7.5, 2.5, 1, 'Context\nRetrieval\nAgent', colors['agent'], 8)
create_box(12.5, 7.5, 2.5, 1, 'Response\nSynthesis\nAgent', colors['agent'], 8)

# Advanced Retrieval Layer
create_box(1, 6, 14, 1, 'Advanced Retrieval Techniques\n(Hybrid Search, Query Expansion, Multi-Hop, Metadata Filtering, Conversational, Classification-Enhanced, Ensemble)', colors['agent'], 8)

# Data Processing Layer
create_box(0.5, 4.5, 3, 1, 'Document\nChunking\n(1000-char chunks,\n250-char overlap)', colors['backend'], 8)
create_box(4, 4.5, 3, 1, 'Embedding\nGeneration\n(OpenAI text-\nembedding-3-small)', colors['backend'], 8)
create_box(7.5, 4.5, 3, 1, 'Vector\nDatabase\n(Qdrant)', colors['database'], 8)
create_box(11, 4.5, 3, 1, 'Metadata\nStorage\n(Document Type,\nCompliance Framework,\nRisk Level)', colors['database'], 8)

# LLM Layer
create_box(6, 3, 4, 1, 'OpenAI GPT-4\n(Reasoning & Response Generation)', colors['external'], 9)

# Evaluation Layer
create_box(0.5, 1.5, 3, 1, 'RAGAS\nEvaluation\n(Faithfulness,\nRelevancy,\nPrecision, Recall)', colors['output'], 8)
create_box(4, 1.5, 3, 1, 'Performance\nMonitoring\n(LangSmith)', colors['output'], 8)
create_box(7.5, 1.5, 3, 1, 'Quality\nAssessment\n(Success Rate,\nResponse Length,\nExecution Time)', colors['output'], 8)
create_box(11, 1.5, 3, 1, 'Business\nImpact\n(Classification\nAccuracy,\nCompliance\nRelevance)', colors['output'], 8)

# Decision Points
create_box(6.5, 5.5, 3, 0.8, 'Document Type\nClassification\nDecision', colors['decision'], 8)

# Arrows - User Flow
create_arrow(1.75, 10.5, 4, 10.5, 'Upload Document')
create_arrow(8, 10.5, 8, 9.5, 'API Request')
create_arrow(8, 9, 8, 8, 'Orchestrate Workflow')

# Arrows - Agent Flow
create_arrow(1.75, 7.5, 3.5, 7.5, 'Process & Chunk')
create_arrow(4.75, 7.5, 6.5, 7.5, 'Classify Document')
create_arrow(7.75, 7.5, 9.5, 7.5, 'Analyze Question')
create_arrow(10.75, 7.5, 12.5, 7.5, 'Retrieve Context')
create_arrow(13.75, 7.5, 13.75, 6.5, 'Synthesize Response')

# Arrows - Data Flow
create_arrow(2, 7.5, 2, 6.5, 'Extract Text')
create_arrow(2, 6, 2, 5.5, 'Generate Chunks')
create_arrow(2, 4.5, 4, 4.5, 'Create Embeddings')
create_arrow(5.5, 4.5, 7.5, 4.5, 'Store Vectors')
create_arrow(9, 4.5, 11, 4.5, 'Store Metadata')

# Arrows - Retrieval Flow
create_arrow(8, 6, 8, 5.5, 'Advanced Retrieval')
create_arrow(8, 5.5, 8, 5.1, 'Query Processing')

# Arrows - LLM Integration
create_arrow(8, 4, 8, 3.5, 'Generate Response')

# Arrows - Evaluation Flow
create_arrow(2, 4.5, 2, 2.5, 'Evaluate Quality')
create_arrow(5.5, 4.5, 5.5, 2.5, 'Monitor Performance')
create_arrow(9, 4.5, 9, 2.5, 'Assess Performance')
create_arrow(12.5, 4.5, 12.5, 2.5, 'Measure Impact')

# Arrows - External Integration
create_arrow(14.25, 10.5, 14.25, 8, 'Regulatory Guidance')
create_arrow(14.25, 7.5, 14.25, 6.5, 'Enhance Response')

# Arrows - Response Flow
create_arrow(8, 3, 8, 2.5, 'Return Response')
create_arrow(8, 2.5, 8, 2, 'Display Results')

# Add legend
legend_elements = [
    patches.Patch(color=colors['user'], label='User Interface'),
    patches.Patch(color=colors['frontend'], label='Frontend'),
    patches.Patch(color=colors['backend'], label='Backend'),
    patches.Patch(color=colors['agent'], label='AI Agents'),
    patches.Patch(color=colors['database'], label='Data Storage'),
    patches.Patch(color=colors['external'], label='External APIs'),
    patches.Patch(color=colors['decision'], label='Decision Points'),
    patches.Patch(color=colors['output'], label='Evaluation & Output')
]

ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))

# Add performance metrics
ax.text(0.5, 0.5, 'PERFORMANCE METRICS:\n• Success Rate: 100% (Both Baseline & Advanced)\n• Response Quality: 1,478-1,651 chars (+12% improvement)\n• RAGAS Scores: Faithfulness 0.850, Relevancy 0.780\n• Classification Accuracy: 95%+\n• Execution Time: 28-36 seconds (Quality-focused)', 
        fontsize=9, bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

plt.tight_layout()
plt.savefig('verityn_ai_flowchart.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('verityn_ai_flowchart.jpg', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

print("✅ Flowchart generated successfully!")
print("📁 Files created:")
print("   - verityn_ai_flowchart.png")
print("   - verityn_ai_flowchart.jpg") 