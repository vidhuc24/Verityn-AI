import { useState, useEffect } from 'react'
import { Send, Lightbulb, MessageSquare } from 'lucide-react'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface ChatInterfaceProps {
  document: any
  analysisResults: any
  documentId: string | null
  selectedQuestion?: string | null
  onQuestionSent?: () => void
}

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  sources?: any[]
  confidence?: number
}

// Helper function to format AI responses
const formatAIResponse = (content: string): string => {
  // If content already has markdown headers, return as is
  if (content.includes('## ')) {
    return content
  }
  
  // If content is plain text, format it nicely
  const lines = content.split('\n').filter(line => line.trim())
  
  if (lines.length === 1) {
    // Single line response
    return content
  }
  
  // Multi-line response - add some structure
  let formatted = ''
  
  // Check if it looks like a list
  if (lines.some(line => line.trim().startsWith('-') || line.trim().startsWith('•'))) {
    formatted = '## 📋 Response\n\n' + content
  } else if (lines.length > 3) {
    // Long response - add structure
    formatted = '## 📋 Analysis\n\n' + content
  } else {
    // Short response - keep as is
    formatted = content
  }
  
  return formatted
}

export default function ChatInterface({ 
  document, 
  analysisResults, 
  documentId, 
  selectedQuestion,
  onQuestionSent 
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: `## 📋 Welcome to Verityn AI

I've analyzed your **${analysisResults.documentType}** document and I'm ready to help you understand the compliance findings, identify risks, and answer questions about the audit results.

## 🔍 What I Can Help With
- **Compliance Analysis**: Identify SOX controls, PCI-DSS requirements, and other frameworks
- **Risk Assessment**: Evaluate material weaknesses and control deficiencies  
- **Audit Findings**: Explain specific findings and their implications
- **Recommendations**: Provide actionable remediation steps
- **Document Navigation**: Help you find specific sections and references

## 🎯 Getting Started
Ask me anything about your document! I can help with questions like:
- "What are the main compliance issues identified?"
- "Which SOX controls are deficient?"
- "What are the material weaknesses?"
- "What remediation steps are recommended?"

What would you like to know about your audit document?`,
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [showQuestions, setShowQuestions] = useState(false)

  // Handle selected question from smart questions
  useEffect(() => {
    if (selectedQuestion && documentId) {
      setInputValue(selectedQuestion)
      // Auto-send the selected question
      handleSend(selectedQuestion)
    }
  }, [selectedQuestion, documentId])

  const handleSend = async (message?: string) => {
    const textToSend = message || inputValue.trim()
    if (!textToSend || !documentId) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: textToSend,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Temporary mock response system for testing UI
      // TODO: Replace with actual API call when backend is ready
      setTimeout(() => {
        const mockResponses = {
          "what is the overall risk assessment": `## 📊 Overall Risk Assessment

Based on my analysis of your **${analysisResults.documentType}** document, here's the comprehensive risk assessment:

### 🚨 **Risk Level: MEDIUM-HIGH**

**Key Risk Factors Identified:**
- **Access Control Deficiencies**: 3 critical findings
- **Segregation of Duties Issues**: 2 material weaknesses  
- **Documentation Gaps**: Incomplete control documentation
- **Monitoring Weaknesses**: Limited ongoing monitoring

### 📈 **Risk Breakdown:**
- **High Risk (3)**: Access management, privileged accounts, system controls
- **Medium Risk (2)**: Documentation, monitoring processes
- **Low Risk (1)**: Training and awareness

### 🎯 **Immediate Actions Required:**
1. Review and restrict excessive user privileges
2. Implement proper segregation of duties controls
3. Enhance control documentation and procedures
4. Establish ongoing monitoring mechanisms

The overall risk score is **7.2/10**, indicating significant control weaknesses that require immediate attention.`,

          "which controls are deficient and what are the implications": `## 🔍 Control Deficiency Analysis

I've identified several critical control deficiencies in your **${analysisResults.documentType}** document:

### ❌ **Critical Control Deficiencies:**

**1. Access Management Controls**
- **Finding**: Excessive user privileges not properly restricted
- **Implication**: Unauthorized access to sensitive systems and data
- **Risk**: High - Potential data breaches and compliance violations

**2. Segregation of Duties**
- **Finding**: Users have conflicting responsibilities
- **Implication**: Increased fraud risk and control bypass opportunities
- **Risk**: High - Material weakness in internal controls

**3. System Security Controls**
- **Finding**: Inadequate password policies and access logging
- **Implication**: Weak security posture and limited audit trails
- **Risk**: Medium-High - Security vulnerabilities and compliance gaps

### 📋 **Compliance Implications:**
- **SOX 404**: Material weakness in internal controls
- **Regulatory Risk**: Potential enforcement actions
- **Financial Impact**: Increased audit costs and potential penalties
- **Reputation Risk**: Loss of stakeholder confidence

### 🚀 **Recommended Remediation:**
1. Implement role-based access controls (RBAC)
2. Establish clear segregation of duties matrix
3. Enhance system security and monitoring
4. Regular access reviews and control testing`,

          "what are the main compliance issues identified": `## ⚠️ Main Compliance Issues Identified

Based on my analysis of your **${analysisResults.documentType}** document, here are the primary compliance concerns:

### 🚨 **Critical Compliance Issues:**

**1. SOX 404 - Internal Control Weaknesses**
- **Issue**: Material weaknesses in access controls
- **Impact**: Non-compliance with financial reporting requirements
- **Deadline**: Must be resolved before next reporting cycle

**2. Access Control Framework Gaps**
- **Issue**: Inadequate user access management
- **Impact**: Violation of data protection requirements
- **Risk**: Regulatory penalties and audit findings

**3. Documentation Compliance Failures**
- **Issue**: Incomplete control documentation
- **Impact**: Non-compliance with audit requirements
- **Consequence**: Increased audit scrutiny and costs

### 📊 **Compliance Status:**
- **Overall Score**: 65% (Below acceptable threshold)
- **Critical Issues**: 3
- **High Priority**: 2
- **Medium Priority**: 1

### ⏰ **Timeline for Resolution:**
- **Immediate (30 days)**: Critical access control issues
- **Short-term (90 days)**: Documentation and process improvements
- **Medium-term (6 months)**: Control testing and validation

### 🎯 **Next Steps:**
1. Prioritize critical compliance gaps
2. Develop remediation action plans
3. Implement interim controls where possible
4. Schedule follow-up compliance reviews`
        }

        // Check for exact matches first, then partial matches
        let response = mockResponses[textToSend.toLowerCase()]
        
        if (!response) {
          // Try partial matching
          for (const [key, value] of Object.entries(mockResponses)) {
            if (textToSend.toLowerCase().includes(key) || key.includes(textToSend.toLowerCase())) {
              response = value
              break
            }
          }
        }

        // Default response if no match found
        if (!response) {
          response = `## 💬 Response to: "${textToSend}"

I understand you're asking about **${textToSend}** regarding your **${analysisResults.documentType}** document.

### 🔍 **What I Can Tell You:**
Based on the document analysis, I can provide insights on:
- Compliance findings and control deficiencies
- Risk assessments and material weaknesses
- Remediation recommendations and timelines
- Specific framework requirements (${analysisResults.complianceFramework || 'SOX'})

### 💡 **Try Asking:**
- "What are the main compliance issues identified?"
- "Which controls are deficient and what are the implications?"
- "What is the overall risk assessment?"
- "What remediation steps are recommended?"

This will help me provide more specific and actionable information about your document.`
        }

        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: response,
          timestamp: new Date()
        }

        setMessages(prev => [...prev, aiMessage])
        setIsLoading(false)
        
        if (onQuestionSent) {
          onQuestionSent()
        }
      }, 1500) // Simulate API delay

      // Comment out the actual API call for now
      /*
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: textToSend,
          document_id: documentId,
          conversation_id: conversationId
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data.response || 'I apologize, but I encountered an error processing your request.',
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence
      }

      setMessages(prev => [...prev, aiMessage])
      
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id)
      }

      if (onQuestionSent) {
        onQuestionSent()
      }
      */

    } catch (error) {
      console.error('Failed to send message:', error)
      toast.error('Failed to send message. Please try again.')
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Generate contextual questions based on document type and framework
  const generateQuestions = () => {
    const baseQuestions = [
      "What are the main compliance issues identified in this document?",
      "Which controls are deficient and what are the implications?",
      "What remediation steps are recommended?",
      "What is the overall risk assessment?",
      "Are there any material weaknesses identified?"
    ]

    const typeSpecificQuestions = {
      'access review': [
        "What access control deficiencies were found?",
        "Which users have excessive privileges?",
        "What segregation of duties issues exist?",
        "How many orphaned accounts were identified?"
      ],
      'risk assessment': [
        "What are the highest risk areas identified?",
        "Which controls are most critical?",
        "What is the likelihood vs impact analysis?",
        "Are there any emerging risks mentioned?"
      ],
      'financial reconciliation': [
        "What reconciliation discrepancies exist?",
        "Which accounts have outstanding items?",
        "What is the financial impact of findings?",
        "Are there any material misstatements?"
      ]
    }

    const frameworkSpecificQuestions = {
      'sox': [
        "Which SOX controls are deficient?",
        "What are the control objectives not met?",
        "Are there any material weaknesses in internal controls?",
        "What is the impact on financial reporting?"
      ],
      'pci-dss': [
        "Which PCI-DSS requirements are not met?",
        "What are the data security gaps?",
        "Are there any vulnerabilities in cardholder data handling?",
        "What is the compliance level assessment?"
      ],
      'iso 27001': [
        "Which information security controls are weak?",
        "What are the security policy gaps?",
        "Are there any asset management issues?",
        "What is the risk treatment status?"
      ]
    }

    const type = analysisResults.documentType?.toLowerCase() || ''
    const framework = analysisResults.complianceFramework?.toLowerCase() || ''

    let questions = [...baseQuestions]

    // Add type-specific questions
    for (const [key, typeQuestions] of Object.entries(typeSpecificQuestions)) {
      if (type.includes(key)) {
        questions = [...questions, ...typeQuestions]
        break
      }
    }

    // Add framework-specific questions
    for (const [key, frameworkQuestions] of Object.entries(frameworkSpecificQuestions)) {
      if (framework.includes(key)) {
        questions = [...questions, ...frameworkQuestions]
        break
      }
    }

    return questions.slice(0, 8) // Limit to 8 questions
  }

  const questions = generateQuestions()

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Header with Smart Questions Button */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold" style={{ color: '#E0E0E0' }}>AI Assistant</h3>
        
        {/* Smart Questions Button */}
        <div className="relative">
          <button
            onClick={() => setShowQuestions(!showQuestions)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-[#9600FF]/10"
            style={{ 
              backgroundColor: showQuestions ? '#9600FF20' : 'transparent',
              border: '1px solid #9600FF',
              color: '#9600FF'
            }}
          >
            <Lightbulb className="h-4 w-4" />
            <span className="text-sm font-medium">Smart Questions</span>
          </button>
          
          {/* Questions Dropdown */}
          {showQuestions && (
            <div className="absolute top-full right-0 mt-2 w-80 p-4 rounded-lg border z-10"
                 style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
              <div className="space-y-2">
                {questions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setShowQuestions(false)
                      setInputValue(question)
                      handleSend(question)
                    }}
                    className="w-full text-left p-3 rounded-lg transition-all duration-200 hover:bg-[#9600FF]/10"
                    style={{ 
                      backgroundColor: '#282828',
                      color: '#E0E0E0',
                      border: '1px solid #A0A0A0'
                    }}
                  >
                    <div className="flex items-start space-x-2">
                      <MessageSquare className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: '#9600FF' }} />
                      <p className="text-sm">{question}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Messages Area - Takes majority of container with scrolling */}
      <div className="flex-1 overflow-y-auto mb-4 p-4 rounded-lg min-h-0 chat-scrollbar" 
           style={{ backgroundColor: '#1A1A1A' }}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-4 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-[#9600FF] text-white'
                    : 'bg-[#282828] text-[#E0E0E0]'
                }`}
              >
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h2: ({children}) => (
                      <h2 className="text-lg font-semibold mt-4 mb-2 first:mt-0 border-b pb-2" 
                           style={{ color: '#E0E0E0', borderColor: '#A0A0A0' }}>
                        {children}
                      </h2>
                    ),
                    h3: ({children}) => (
                      <h3 className="text-base font-medium mt-3 mb-1" style={{ color: '#E0E0E0' }}>
                        {children}
                      </h3>
                    ),
                    p: ({children}) => (
                      <p className="text-sm mb-2 last:mb-0" style={{ color: '#E0E0E0' }}>
                        {children}
                      </p>
                    ),
                    ul: ({children}) => (
                      <ul className="list-disc list-inside space-y-1 my-2 ml-4">
                        {children}
                      </ul>
                    ),
                    ol: ({children}) => (
                      <ol className="list-decimal list-inside space-y-1 my-2 ml-4">
                        {children}
                      </ol>
                    ),
                    li: ({children}) => (
                      <li className="text-sm" style={{ color: '#E0E0E0' }}>
                        {children}
                      </li>
                    ),
                    strong: ({children}) => (
                      <strong className="font-semibold" style={{ color: '#E0E0E0' }}>
                        {children}
                      </strong>
                    ),
                    em: ({children}) => (
                      <em className="italic" style={{ color: '#A0A0A0' }}>
                        {children}
                      </em>
                    ),
                    blockquote: ({children}) => (
                      <blockquote className="border-l-4 pl-4 py-2 my-3 rounded-r-lg" 
                                 style={{ borderColor: '#9600FF', backgroundColor: '#1A1A1A' }}>
                        {children}
                      </blockquote>
                    ),
                    code: ({children}) => (
                      <code className="px-1.5 py-0.5 rounded text-xs font-mono" 
                            style={{ backgroundColor: '#1A1A1A', color: '#E0E0E0' }}>
                        {children}
                      </code>
                    ),
                    pre: ({children}) => (
                      <pre className="p-3 rounded-lg text-xs font-mono overflow-x-auto my-3" 
                            style={{ backgroundColor: '#1A1A1A', color: '#E0E0A0' }}>
                        {children}
                      </pre>
                    ),
                  }}
                >
                  {formatAIResponse(message.content)}
                </ReactMarkdown>
                
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-white/20">
                    <p className="text-xs opacity-80 mb-2">Sources:</p>
                    <div className="space-y-1">
                      {message.sources.map((source: any, index: number) => (
                        <p key={index} className="text-xs opacity-70">
                          {source.title || source.filename || `Source ${index + 1}`}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
                
                <p className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[#282828] text-[#E0E0E0] p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-[#9600FF] border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="flex items-end space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
        <div className="flex-1">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about this document..."
            className="w-full p-3 rounded-lg resize-none"
            style={{ 
              backgroundColor: '#282828',
              color: '#E0E0E0',
              border: '1px solid #A0A0A0'
            }}
            rows={2}
          />
        </div>
        <button
          onClick={() => handleSend()}
          disabled={!inputValue.trim() || isLoading}
          className="p-3 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ 
            backgroundColor: inputValue.trim() ? '#9600FF' : '#A0A0A0',
            color: 'white'
          }}
        >
          <Send className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
} 