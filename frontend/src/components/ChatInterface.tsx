import { useState, useEffect } from 'react'
import { Send } from 'lucide-react'
import toast from 'react-hot-toast'

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
      content: `I've analyzed your ${analysisResults.documentType} document. I can help you understand the compliance findings, identify risks, and answer questions about the audit results. What would you like to know?`,
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
        content: result.chat.response,
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
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
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
                className={`max-w-3xl rounded-lg px-4 py-2 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                
                {/* Show sources for AI messages */}
                {message.type === 'ai' && message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Sources:</p>
                    {message.sources.map((source: any, index: number) => (
                      <p key={index} className="text-xs text-gray-600">
                        • {source.title || source.content?.substring(0, 50)}...
                      </p>
                    ))}
                  </div>
                )}
                
                {/* Show confidence for AI messages */}
                {message.type === 'ai' && message.confidence && (
                  <div className="mt-1">
                    <p className="text-xs text-gray-500">
                      Confidence: {(message.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                
                <p className={`text-xs mt-1 ${
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