import { useState, useRef } from 'react'
import { Upload } from 'lucide-react'

interface DocumentUploadProps {
  onUpload: (file: File) => void
  isUploading: boolean
  uploadedDocument: any
}

export default function DocumentUpload({ onUpload, isUploading, uploadedDocument }: DocumentUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      onUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onUpload(files[0])
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  if (isUploading) {
    return (
      <div className="mb-6">
        <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Upload Document</h3>
        <div className="border-2 border-dashed rounded-xl p-8 text-center" style={{ borderColor: '#A0A0A0' }}>
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 border-2 border-[#9600FF] border-t-transparent rounded-full animate-spin mx-auto"></div>
            <div className="space-y-2">
              <p className="text-lg font-medium" style={{ color: '#E0E0E0' }}>Processing document...</p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>This may take a few moments</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mb-6">
      <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Upload Document</h3>
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 ${
          isDragOver ? 'border-[#9600FF] bg-[#9600FF]/10' : 'border-[#A0A0A0] hover:border-[#9600FF]/70'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.doc,.docx,.txt,.csv,.xlsx"
          onChange={handleFileSelect}
        />
        
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-[#9600FF] to-[#4600C8] flex items-center justify-center">
            <Upload className="w-6 h-6 text-white" />
          </div>
          <div>
            <p style={{ color: '#E0E0E0' }}>
              Drop your document here
            </p>
            <p className="text-sm mt-1" style={{ color: '#A0A0A0' }}>
              or click to browse files
            </p>
          </div>
          <p className="text-xs" style={{ color: '#A0A0A0' }}>
            Supports PDF, DOC, DOCX, TXT, CSV, XLSX
          </p>
        </div>
      </div>
      
      {uploadedDocument && (
        <div className="mt-4 p-3 rounded-lg" style={{ backgroundColor: '#9600FF', color: 'white' }}>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-white rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-[#9600FF] rounded-full"></div>
            </div>
            <span className="text-sm font-medium">Document uploaded successfully</span>
          </div>
        </div>
      )}
    </div>
  )
} 