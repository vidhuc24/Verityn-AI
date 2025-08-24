import { FileText, CheckCircle2 } from 'lucide-react';

interface DocumentDisplayProps {
  uploadedDocument: string | null;
}

export function DocumentDisplay({ uploadedDocument }: DocumentDisplayProps) {
  if (!uploadedDocument) {
    return (
      <div className="flex-1 rounded-xl border-2 border-dashed border-[#A0A0A0]/30 p-6 flex items-center justify-center">
        <p style={{ color: '#A0A0A0' }}>No document uploaded</p>
      </div>
    );
  }

  return (
    <div className="flex-1">
      <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Uploaded Document</h3>
      <div className="rounded-xl border border-[#A0A0A0]/30 p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-[#9600FF] to-[#4600C8] flex items-center justify-center">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <p style={{ color: '#E0E0E0' }}>{uploadedDocument}</p>
            <p className="text-sm" style={{ color: '#A0A0A0' }}>
              Uploaded just now
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 text-sm">
          <CheckCircle2 className="w-4 h-4 text-green-500" />
          <span style={{ color: '#A0A0A0' }}>Processing complete</span>
        </div>
        
        <div className="mt-4 p-3 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
          <p className="text-sm" style={{ color: '#A0A0A0' }}>
            Document successfully analyzed. Ready for compliance review and Q&A.
          </p>
        </div>
      </div>
    </div>
  );
}