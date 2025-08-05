import { useState } from 'react'
import toast from 'react-hot-toast'

interface DocumentUploadProps {
  onUpload: (file: File) => void
  isUploading: boolean
  uploadedDocument: any
}

export default function DocumentUpload({ onUpload, isUploading, uploadedDocument }: DocumentUploadProps) {
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFile = (file: File) => {
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.txt', '.csv', '.xlsx']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(fileExtension)) {
      toast.error('Invalid file type. Please upload PDF, DOCX, TXT, CSV, or XLSX files.')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size too large. Please upload files smaller than 10MB.')
      return
    }

    onUpload(file)
  }

  return (
    <div className="card">
      <div className="text-center py-12">
        <div 
          className={`border-2 border-dashed rounded-lg p-8 transition-colors ${
            dragActive 
              ? 'border-blue-400 bg-blue-50' 
              : 'border-gray-300'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {isUploading ? (
            <div>
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Processing document...</p>
              <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
            </div>
          ) : (
            <div>
              <div className="mb-4">
                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                Upload Document
              </p>
              <p className="text-gray-600 mb-4">
                Drag and drop your audit document here, or click to browse
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Supports PDF, DOCX, TXT, CSV, XLSX (max 10MB)
              </p>
              <input
                type="file"
                accept=".pdf,.docx,.txt,.csv,.xlsx"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFile(file)
                }}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="btn-primary cursor-pointer inline-block"
              >
                Choose File
              </label>
            </div>
          )}
          
          {uploadedDocument && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <p className="text-green-800 font-medium">
                  ✓ {uploadedDocument.name}
                </p>
              </div>
              <p className="text-sm text-green-600 mt-1">
                Document uploaded successfully
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 