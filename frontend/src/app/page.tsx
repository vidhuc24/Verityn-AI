'use client'

import { useState } from 'react'
import toast, { Toaster } from 'react-hot-toast'
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
      
      // For now, use mock data to match the design specifications
      const mockAnalysis = {
        documentType: file.type.includes('pdf') ? 'PDF Document' : 
                      file.type.includes('doc') ? 'Word Document' : 
                      file.type.includes('txt') ? 'Text Document' : 'Document',
        complianceFramework: 'SOX, PCI-DSS',
        complianceScore: 94,
        riskFactors: 3,
        keyRequirements: 12,
        confidence: 0.95,
        ...analysisResult.analysis // Merge with actual backend results if available
      }
      
      setAnalysisResults(mockAnalysis)
      
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
    <div className="min-h-screen overflow-hidden" style={{ backgroundColor: '#1A1A1A' }}>
      {/* Top Banner */}
      <Header />
      
      {/* Main Content Area */}
      <div className="flex gap-4 p-6 h-[calc(100vh-56px)] overflow-hidden">
        {/* Left Container - Narrowed to ~20-25% */}
        <div className="w-[22%] flex flex-col gap-4 overflow-hidden">
          <div className="rounded-2xl p-6 h-full flex flex-col overflow-hidden" style={{ backgroundColor: '#282828' }}>
            <DocumentUpload 
              onUpload={handleDocumentUpload}
              isUploading={isAnalyzing}
              uploadedDocument={uploadedDocument}
            />
            
            {/* Document Status - Simple text as per design */}
            {!uploadedDocument && !isAnalyzing && (
              <div className="flex-1 flex items-center justify-center">
                <p style={{ color: '#A0A0A0' }}>No document uploaded</p>
              </div>
            )}
            
            {/* Document Display - Only show when document is uploaded */}
            {uploadedDocument && (
              <div className="flex-1 overflow-hidden">
                <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Document Info</h3>
                <div className="p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
                  <p className="text-sm" style={{ color: '#E0E0E0' }}>
                    <strong>Name:</strong> {uploadedDocument.name.replace(/\.[^/.]+$/, '')}
                  </p>
                  <p className="text-sm mt-2" style={{ color: '#A0A0A0' }}>
                    <strong>Type:</strong> {uploadedDocument.type.split('/')[1] || uploadedDocument.type}
                  </p>
                  <p className="text-sm mt-2" style={{ color: '#A0A0A0' }}>
                    <strong>Size:</strong> {uploadedDocument.size > 1024 * 1024 
                      ? `${(uploadedDocument.size / 1024 / 1024).toFixed(2)} MB`
                      : `${(uploadedDocument.size / 1024).toFixed(2)} KB`
                    }
                  </p>
                  <p className="text-sm mt-2" style={{ color: '#A0A0A0' }}>
                    <strong>Framework:</strong> SOX
                  </p>
                  <p className="text-sm mt-2" style={{ color: '#A0A0A0' }}>
                    <strong>Category:</strong> Access Review
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Right Container - Expanded to ~78% */}
        <div className="w-[78%] flex flex-col gap-4 overflow-hidden">
          <div className="rounded-2xl p-6 h-full flex flex-col overflow-hidden" style={{ backgroundColor: '#282828' }}>
            {/* Analysis Cards */}
            {(analysisResults || isAnalyzing) && (
              <div className="mb-2 flex-shrink-0">
                <AnalysisPanel 
                  results={analysisResults}
                  isAnalyzing={isAnalyzing}
                />
              </div>
            )}

            {/* Chat Area - Takes majority of container */}
            {analysisResults && (
              <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                <ChatInterface 
                  document={uploadedDocument}
                  analysisResults={analysisResults}
                  documentId={documentId}
                  selectedQuestion={selectedQuestion}
                  onQuestionSent={() => setSelectedQuestion(null)}
                />
              </div>
            )}
          </div>
        </div>
      </div>
      
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#282828',
            color: '#E0E0E0',
            border: '1px solid #A0A0A0',
          },
        }}
      />
    </div>
  )
} 