import { useState, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

interface DocumentUploadProps {
  onDocumentUpload: (fileName: string) => void;
}

export function DocumentUpload({ onDocumentUpload }: DocumentUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onDocumentUpload(files[0].name);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onDocumentUpload(files[0].name);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

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
          accept=".pdf,.doc,.docx,.txt"
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
            Supports PDF, DOC, DOCX, TXT
          </p>
        </div>
      </div>
    </div>
  );
}