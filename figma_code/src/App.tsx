import { useState } from 'react';
import { TopBanner } from './components/TopBanner';
import { DocumentUpload } from './components/DocumentUpload';
import { DocumentDisplay } from './components/DocumentDisplay';
import { AnalysisCards } from './components/AnalysisCards';
import { ChatArea } from './components/ChatArea';

export default function App() {
  const [uploadedDocument, setUploadedDocument] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{id: string, text: string, sender: 'user' | 'ai'}>>([]);

  const handleDocumentUpload = (fileName: string) => {
    setUploadedDocument(fileName);
  };

  const handleSendMessage = (message: string) => {
    const userMessage = { id: Date.now().toString(), text: message, sender: 'user' as const };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const aiMessage = { 
        id: (Date.now() + 1).toString(), 
        text: "I've analyzed your document. Based on the content, I can help you with compliance requirements and key insights.", 
        sender: 'ai' as const 
      };
      setChatMessages(prev => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#1A1A1A' }}>
      {/* Top Banner */}
      <TopBanner />
      
      {/* Main Content Area */}
      <div className="flex gap-6 p-6 h-[calc(100vh-80px)]">
        {/* Left Container */}
        <div className="w-[30%] flex flex-col gap-6">
          <div className="rounded-2xl p-6 h-full flex flex-col" style={{ backgroundColor: '#282828' }}>
            <DocumentUpload onDocumentUpload={handleDocumentUpload} />
            <DocumentDisplay uploadedDocument={uploadedDocument} />
          </div>
        </div>
        
        {/* Right Container */}
        <div className="w-[70%] flex flex-col gap-6">
          <div className="rounded-2xl p-6 h-full flex flex-col" style={{ backgroundColor: '#282828' }}>
            <AnalysisCards />
            <ChatArea 
              messages={chatMessages}
              onSendMessage={handleSendMessage}
            />
          </div>
        </div>
      </div>
    </div>
  );
}