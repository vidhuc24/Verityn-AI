#!/usr/bin/env python3
"""
Create Verityn AI Application Flowchart (Clean Mermaid Version)
Generates a Mermaid flowchart without emojis or special characters for compatibility.
"""

def create_clean_mermaid_flowchart():
    mermaid_code = """
graph TB
    %% Title
    subgraph "VERITYN AI - MULTI-AGENT DOCUMENT CHAT SYSTEM"
    
    %% User Interface Layer
    subgraph "User Interface Layer"
        A[User/Auditor<br/>• Upload Document<br/>• Ask Questions<br/>• View Results]
        B[Next.js Frontend<br/>• Document Upload<br/>• Chat Interface<br/>• Smart Questions<br/>• Progress Feedback]
        C[FastAPI Backend<br/>• Multi-Agent Orchestration<br/>• API Endpoints<br/>• Error Handling]
    end
    
    %% Multi-Agent Workflow Layer
    subgraph "Multi-Agent Workflow"
        D[Document Processing Agent<br/>• Extract Text<br/>• Chunk Content<br/>• Generate Embeddings]
        E[Classification Agent<br/>• Identify Type<br/>• SOX Controls<br/>• Risk Level<br/>• Compliance Framework]
        F[Question Analysis Agent<br/>• Understand Intent<br/>• Optimize Query<br/>• Context Awareness]
        G[Context Retrieval Agent<br/>• Hybrid Search<br/>• Query Expansion<br/>• Multi-Hop<br/>• Metadata Filtering]
        H[Response Synthesis Agent<br/>• Combine Context<br/>• Generate Response<br/>• Source Citations]
        I[Compliance Analyzer Agent<br/>• Risk Assessment<br/>• Compliance Validation<br/>• Control Mapping]
    end
    
    %% Advanced Retrieval Layer
    subgraph "Advanced Retrieval Techniques"
        J1[Hybrid Search<br/>Semantic + Keyword]
        J2[Query Expansion<br/>Audit Terminology]
        J3[Multi-Hop Retrieval<br/>Comprehensive Analysis]
        J4[Metadata Filtering<br/>Type, Framework, Risk]
        J5[Conversational Retrieval<br/>Context Preservation]
        J6[Classification-Enhanced<br/>Type-Specific Optimization]
        J7[Ensemble Retrieval<br/>Multiple Techniques]
    end
    
    %% Data Processing Layer
    subgraph "Data Processing Layer"
        K[Document Chunking<br/>• 1000-char chunks<br/>• 250-char overlap<br/>• Preserve Structure]
        L[Embedding Generation<br/>• OpenAI text-embedding-3-small<br/>• Semantic Vectors<br/>• High Quality]
        M[Vector Database - Qdrant<br/>• Similarity Search<br/>• Fast Retrieval<br/>• Metadata Storage]
        N[Metadata Storage<br/>• Document Type<br/>• Compliance Framework<br/>• Risk Level<br/>• Company Info]
    end
    
    %% LLM Integration
    subgraph "LLM Integration"
        O[OpenAI GPT-4<br/>• Superior Reasoning<br/>• Compliance Analysis<br/>• Response Generation<br/>• Context Awareness]
    end
    
    %% External Integrations
    subgraph "External Integrations"
        P[Tavily API<br/>• Real-time Regulatory Guidance<br/>• Current Compliance Info<br/>• Best Practices<br/>• Framework Updates]
    end
    
    %% Evaluation & Monitoring
    subgraph "Evaluation & Monitoring"
        R[RAGAS Evaluation<br/>• Faithfulness: 0.850<br/>• Relevancy: 0.780<br/>• Precision: 0.820<br/>• Recall: 0.750]
        S[Performance Monitoring - LangSmith<br/>• Real-time Metrics<br/>• Performance Tracking<br/>• Debugging<br/>• Optimization]
        T[Quality Assessment<br/>• Success Rate: 100%<br/>• Response Length: 1,478-1,651 chars<br/>• Execution Time: 28-36s]
        U[Business Impact<br/>• Classification Accuracy: 95%+<br/>• Compliance Relevance: 90%+<br/>• Risk Identification: 85%+<br/>• Production Ready]
    end
    
    %% Performance Metrics Summary
    subgraph "Performance Metrics Summary"
        V[Key Achievements<br/>• 100% Success Rate (Both Systems)<br/>• 12% Response Quality Improvement<br/>• Production-Ready Stability<br/>• Quality-Focused Approach<br/>• Comprehensive Evaluation]
    end
    
    end
    
    %% Flow Connections
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    G --> J1
    G --> J2
    G --> J3
    G --> J4
    G --> J5
    G --> J6
    G --> J7
    D --> K
    K --> L
    L --> M
    M --> N
    H --> O
    I --> O
    O --> P
    P --> H
    H --> R
    I --> S
    H --> T
    I --> U
    R --> V
    S --> V
    T --> V
    U --> V
    
    %% Styling
    classDef userInterface fill:#E3F2FD,stroke:#1976D2,stroke-width:3px,color:#000
    classDef backend fill:#E8F5E8,stroke:#388E3C,stroke-width:3px,color:#000
    classDef agent fill:#FFF3E0,stroke:#F57C00,stroke-width:3px,color:#000
    classDef retrieval fill:#FFF8E1,stroke:#FFA000,stroke-width:3px,color:#000
    classDef database fill:#FCE4EC,stroke:#C2185B,stroke-width:3px,color:#000
    classDef external fill:#F1F8E9,stroke:#689F38,stroke-width:3px,color:#000
    classDef evaluation fill:#F9FBE7,stroke:#AFB42B,stroke-width:3px,color:#000
    classDef metrics fill:#E0F2F1,stroke:#00695C,stroke-width:3px,color:#000
    
    class A,B userInterface
    class C,D,E,F,G,H,I,K,L backend
    class J1,J2,J3,J4,J5,J6,J7 retrieval
    class M,N database
    class O,P external
    class R,S,T,U evaluation
    class V metrics
    """
    
    return mermaid_code

def create_simple_clean_flowchart():
    mermaid_code = """
graph TD
    %% User Interface Layer
    A[User/Auditor] --> B[Next.js Frontend]
    B --> C[FastAPI Backend]
    
    %% Multi-Agent Workflow
    C --> D[Document Processing Agent]
    D --> E[Classification Agent]
    E --> F[Question Analysis Agent]
    F --> G[Context Retrieval Agent]
    G --> H[Response Synthesis Agent]
    H --> I[Compliance Analyzer Agent]
    
    %% Advanced Retrieval Techniques
    G --> J1[Hybrid Search]
    G --> J2[Query Expansion]
    G --> J3[Multi-Hop Retrieval]
    G --> J4[Metadata Filtering]
    G --> J5[Conversational Retrieval]
    G --> J6[Classification-Enhanced]
    G --> J7[Ensemble Retrieval]
    
    %% Data Processing Layer
    D --> K[Document Chunking]
    K --> L[Embedding Generation]
    L --> M[Vector Database - Qdrant]
    M --> N[Metadata Storage]
    
    %% LLM Integration
    H --> O[OpenAI GPT-4]
    I --> O
    
    %% External Integrations
    O --> P[Tavily API]
    P --> Q[Regulatory Guidance]
    
    %% Evaluation & Monitoring
    H --> R[RAGAS Evaluation]
    I --> S[Performance Monitoring - LangSmith]
    H --> T[Quality Assessment]
    I --> U[Business Impact]
    
    %% Response Flow
    O --> V[Generate Response]
    V --> W[Return to Frontend]
    W --> X[Display Results]
    
    %% Styling
    classDef userInterface fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef backend fill:#E8F5E8,stroke:#388E3C,stroke-width:2px
    classDef agent fill:#FFF3E0,stroke:#F57C00,stroke-width:2px
    classDef database fill:#FCE4EC,stroke:#C2185B,stroke-width:2px
    classDef external fill:#F1F8E9,stroke:#689F38,stroke-width:2px
    classDef evaluation fill:#F9FBE7,stroke:#AFB42B,stroke-width:2px
    
    class A,B userInterface
    class C,D,E,F,G,H,I,K,L backend
    class J1,J2,J3,J4,J5,J6,J7 agent
    class M,N database
    class O,P,Q external
    class R,S,T,U evaluation
    """
    
    return mermaid_code

if __name__ == "__main__":
    # Create clean detailed version
    detailed_mermaid = create_clean_mermaid_flowchart()
    with open('verityn_ai_flowchart_clean_detailed.mmd', 'w') as f:
        f.write(detailed_mermaid)
    
    # Create clean simple version
    simple_mermaid = create_simple_clean_flowchart()
    with open('verityn_ai_flowchart_clean_simple.mmd', 'w') as f:
        f.write(simple_mermaid)
    
    print("✅ Clean Mermaid flowcharts generated successfully!")
    print("📁 Files created:")
    print("   - verityn_ai_flowchart_clean_detailed.mmd")
    print("   - verityn_ai_flowchart_clean_simple.mmd")
    print("\n💡 These versions are compatible with mermaid.live!")
    print("   No emojis or special characters that cause parsing errors.")
    
    print("\n📋 Clean Detailed Mermaid Code:")
    print("=" * 50)
    print(detailed_mermaid)
    
    print("\n📋 Clean Simple Mermaid Code:")
    print("=" * 50)
    print(simple_mermaid) 