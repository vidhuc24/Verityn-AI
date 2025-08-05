'use client'

import { useState } from 'react'
import toast from 'react-hot-toast'
import Header from '@/components/Header'
import DocumentUpload from '@/components/DocumentUpload'
import AnalysisPanel from '@/components/AnalysisPanel'
import QuestionSuggestions from '@/components/QuestionSuggestions'
import ChatInterface from '@/components/ChatInterface'

export default function Home() {
  const [uploadedDocument, setUploadedDocument] = useState<any>(null)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [documentId, setDocumentId] = useState<string | null>(null)
  const [selectedQuestion, setSelectedQuestion] = useState<string | null>(null)

  const handleDocumentUpload = async (file: File) => {
    setIsAnalyzing(true)
    try {
      // Upload document to backend
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json()
        throw new Error(errorData.error || 'Upload failed')
      }

      const uploadResult = await uploadResponse.json()
      setUploadedDocument({
        name: file.name,
        type: file.type,
        size: file.size,
        id: uploadResult.document?.document_id
      })
      setDocumentId(uploadResult.document?.document_id)

      toast.success('Document uploaded successfully!')

      // Analyze document
      const analysisResponse = await fetch('/api/analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: uploadResult.document?.document_id
        }),
      })

      if (!analysisResponse.ok) {
        const errorData = await analysisResponse.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const analysisResult = await analysisResponse.json()
      setAnalysisResults(analysisResult.analysis)
      
      toast.success('Document analysis completed!')
      
    } catch (error) {
      console.error('Upload/Analysis failed:', error)
      toast.error(error instanceof Error ? error.message : 'Upload failed')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleQuestionSelect = (question: string) => {
    // Set the selected question to be sent to chat interface
    setSelectedQuestion(question)
    toast.success('Question selected! You can now ask it in the chat.')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Document Upload Section */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Upload Document
            </h2>
            <DocumentUpload 
              onUpload={handleDocumentUpload}
              isUploading={isAnalyzing}
              uploadedDocument={uploadedDocument}
            />
          </section>

          {/* Analysis Results Section */}
          {(analysisResults || isAnalyzing) && (
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Document Analysis
              </h2>
              <AnalysisPanel 
                results={analysisResults}
                isAnalyzing={isAnalyzing}
              />
            </section>
          )}

          {/* Question Suggestions Section */}
          {analysisResults && (
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Smart Questions
              </h2>
              <QuestionSuggestions 
                documentType={analysisResults.documentType}
                complianceFramework={analysisResults.complianceFramework}
                onQuestionSelect={handleQuestionSelect}
              />
            </section>
          )}

          {/* Chat Interface Section */}
          {analysisResults && (
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Chat with Document
              </h2>
              <ChatInterface 
                document={uploadedDocument}
                analysisResults={analysisResults}
                documentId={documentId}
                selectedQuestion={selectedQuestion}
                onQuestionSent={() => setSelectedQuestion(null)}
              />
            </section>
          )}
        </div>
      </main>
    </div>
  )
} 