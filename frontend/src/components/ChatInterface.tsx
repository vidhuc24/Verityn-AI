import { useState, useEffect } from 'react'
import { Send } from 'lucide-react'
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

  // Handle selected question from smart questions
  useEffect(() => {
    if (selectedQuestion && documentId) {
      setInputValue(selectedQuestion)
      // Auto-send the selected question
      handleSend(selectedQuestion)
    }
  }, [selectedQuestion, documentId])

  const handleSend = async (questionToSend?: string) => {
    const question = questionToSend || inputValue.trim()
    if (!question || !documentId) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Clear selected question if it was auto-sent
    if (questionToSend && onQuestionSent) {
      onQuestionSent()
    }

    try {
      // Call backend chat API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: question,
          document_id: documentId,
          conversation_id: conversationId
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Chat failed')
      }

      const result = await response.json()
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: formatAIResponse(result.chat.response),
        timestamp: new Date(),
        sources: result.chat.sources,
        confidence: result.chat.confidence
      }

      setMessages(prev => [...prev, aiMessage])
      setConversationId(result.chat.conversation_id)

      // Show success toast with execution time
      if (result.chat.execution_time) {
        toast.success(`Response generated in ${(result.chat.execution_time / 1000).toFixed(1)}s`)
      }

    } catch (error) {
      console.error('Chat error:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to get response')
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: formatAIResponse('Sorry, I encountered an error while processing your question. Please try again.'),
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="card">
      <div className="h-96 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-4xl rounded-lg px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-900 border border-gray-200'
                }`}
              >
                {message.type === 'user' ? (
                  <p className="text-sm">{message.content}</p>
                ) : (
                  <div className="chat-markdown">
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm]}
                      components={{
                        h2: ({children}) => (
                          <h2 className="text-lg font-semibold text-gray-900 mt-4 mb-2 first:mt-0">
                            {children}
                          </h2>
                        ),
                        h3: ({children}) => (
                          <h3 className="text-base font-medium text-gray-800 mt-3 mb-1">
                            {children}
                          </h3>
                        ),
                        ul: ({children}) => (
                          <ul className="list-disc list-inside space-y-1 my-2">
                            {children}
                          </ul>
                        ),
                        ol: ({children}) => (
                          <ol className="list-decimal list-inside space-y-1 my-2">
                            {children}
                          </ol>
                        ),
                        li: ({children}) => (
                          <li className="text-sm text-gray-700">
                            {children}
                          </li>
                        ),
                        p: ({children}) => (
                          <p className="text-sm text-gray-700 mb-2 last:mb-0">
                            {children}
                          </p>
                        ),
                        strong: ({children}) => (
                          <strong className="font-semibold text-gray-900">
                            {children}
                          </strong>
                        ),
                        em: ({children}) => (
                          <em className="italic text-gray-800">
                            {children}
                          </em>
                        ),
                        blockquote: ({children}) => (
                          <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-3 bg-blue-50">
                            {children}
                          </blockquote>
                        ),
                        code: ({children}) => (
                          <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">
                            {children}
                          </code>
                        ),
                        pre: ({children}) => (
                          <pre className="bg-gray-100 p-3 rounded text-xs font-mono overflow-x-auto">
                            {children}
                          </pre>
                        ),
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                )}
                
                {/* Show sources for AI messages */}
                {message.type === 'ai' && message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-2 font-medium">📚 Sources:</p>
                    {message.sources.map((source: any, index: number) => (
                      <p key={index} className="text-xs text-gray-600 mb-1">
                        • {source.title || source.content?.substring(0, 60)}...
                      </p>
                    ))}
                  </div>
                )}
                
                {/* Show confidence for AI messages */}
                {message.type === 'ai' && message.confidence && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500">
                      🎯 Confidence: {(message.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                
                <p className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="animate-pulse flex space-x-1">
                    <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                    <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                  </div>
                  <span className="text-xs text-gray-500">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about this document..."
              className="flex-1 input-field"
              disabled={isLoading || !documentId}
            />
            <button
              onClick={() => handleSend()}
              disabled={!inputValue.trim() || isLoading || !documentId}
              className="btn-primary"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          {!documentId && (
            <p className="text-xs text-gray-500 mt-2">
              Please upload a document first to start chatting
            </p>
          )}
        </div>
      </div>
    </div>
  )
} 