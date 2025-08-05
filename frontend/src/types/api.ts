// API Types for Verityn AI Frontend

export interface DocumentResponse {
  document_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  classification?: DocumentClassification;
  metadata?: DocumentMetadata;
}

export interface DocumentClassification {
  document_type: string;
  confidence: number;
  compliance_frameworks: string[];
  metadata: {
    date?: string;
    department?: string;
    reviewer?: string;
  };
}

export interface DocumentMetadata {
  filename: string;
  file_size: number;
  content_type?: string;
  description?: string;
  upload_timestamp?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: ChatSource[];
  confidence?: number;
}

export interface ChatSource {
  title: string;
  content: string;
  url?: string;
}

export interface ChatRequest {
  message: string;
  document_id?: string;
  conversation_id?: string;
  include_web_search?: boolean;
}

export interface ChatResponse {
  message: ChatMessage;
  conversation_id: string;
  suggested_questions?: string[];
  compliance_insights?: ComplianceInsights;
}

export interface ComplianceInsights {
  frameworks: string[];
  risk_level: 'Low' | 'Medium' | 'High';
  key_findings: string[];
}

export interface QuestionSuggestionRequest {
  document_id: string;
  document_type?: string;
  compliance_framework?: string;
}

export interface QuestionSuggestionResponse {
  questions: string[];
  categories: string[];
  compliance_frameworks: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  services: Record<string, string>;
}

export interface ApiError {
  error: string;
  detail?: string;
  status_code: number;
  path: string;
}

// File upload types
export interface FileUploadResponse {
  success: boolean;
  document?: DocumentResponse;
  error?: string;
}

// Compliance dashboard types
export interface ComplianceMetrics {
  documents_analyzed: number;
  compliance_score: number;
  risk_level: string;
  open_issues: number;
}

export interface ComplianceFramework {
  name: string;
  status: 'Compliant' | 'In Review' | 'Non-Compliant';
  score: number;
}

export interface AuditFinding {
  type: 'Risk' | 'Compliance' | 'Recommendation';
  description: string;
  severity: 'Low' | 'Medium' | 'High';
  framework: string;
  timestamp: string;
} 