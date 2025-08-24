import { useState, useRef, useEffect } from 'react';
import { Send, Lightbulb, X } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
}

interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
}

export function ChatArea({ messages, onSendMessage }: ChatAreaProps) {
  const [inputValue, setInputValue] = useState('');
  const [showSmartQuestions, setShowSmartQuestions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const smartQuestions = [
    "What are the key compliance requirements in this document?",
    "Identify any potential risk factors or red flags",
    "Summarize the main terms and conditions",
    "What regulatory standards does this document address?",
    "Are there any missing compliance elements?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSmartQuestion = (question: string) => {
    onSendMessage(question);
    setShowSmartQuestions(false);
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 style={{ color: '#E0E0E0' }}>AI Assistant</h3>
        
        {/* Smart Questions Button */}
        <div className="relative">
          <button
            onClick={() => setShowSmartQuestions(!showSmartQuestions)}
            className="w-10 h-10 rounded-full bg-gradient-to-r from-[#9600FF] to-[#4600C8] flex items-center justify-center hover:shadow-lg hover:shadow-[#9600FF]/25 transition-all duration-300"
            title="Smart Questions"
          >
            <Lightbulb className="w-5 h-5 text-white" />
          </button>
          
          {/* Smart Questions Overlay */}
          {showSmartQuestions && (
            <div 
              className="absolute top-12 right-0 w-80 rounded-xl border border-[#A0A0A0]/20 p-4 z-10 shadow-xl"
              style={{ backgroundColor: '#282828' }}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 style={{ color: '#E0E0E0' }}>Smart Questions</h4>
                <button
                  onClick={() => setShowSmartQuestions(false)}
                  className="w-6 h-6 rounded-full hover:bg-[#A0A0A0]/20 flex items-center justify-center"
                >
                  <X className="w-4 h-4" style={{ color: '#A0A0A0' }} />
                </button>
              </div>
              <div className="space-y-2">
                {smartQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSmartQuestion(question)}
                    className="w-full text-left p-2 rounded-lg hover:bg-[#9600FF]/10 transition-colors duration-200"
                    style={{ color: '#A0A0A0' }}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Messages Area */}
      <div className="flex-1 rounded-xl border border-[#A0A0A0]/20 p-4 mb-4 overflow-y-auto min-h-0" style={{ backgroundColor: '#1A1A1A' }}>
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p style={{ color: '#A0A0A0' }}>Start a conversation about your document...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-xl p-3 ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-[#9600FF] to-[#4600C8] text-white'
                      : 'border border-[#A0A0A0]/20'
                  }`}
                  style={message.sender === 'ai' ? { backgroundColor: '#282828', color: '#E0E0E0' } : {}}
                >
                  {message.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="flex gap-3">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about your document..."
          className="flex-1 rounded-xl px-4 py-3 border border-[#A0A0A0]/20 focus:border-[#9600FF] focus:outline-none transition-colors duration-200"
          style={{ backgroundColor: '#1A1A1A', color: '#E0E0E0' }}
        />
        <button
          onClick={handleSend}
          disabled={!inputValue.trim()}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#9600FF] to-[#4600C8] text-white hover:shadow-lg hover:shadow-[#9600FF]/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}