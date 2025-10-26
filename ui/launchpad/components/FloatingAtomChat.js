import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';

export default function FloatingAtomChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hi! I\'m ATOM AI. I can help with performance optimization, security analysis, cost reduction, and infrastructure scaling. What would you like to focus on?' }
  ]);
  const [input, setInput] = useState('');
  const [dimensions, setDimensions] = useState({ width: 320, height: 400 });
  const [isResizing, setIsResizing] = useState(false);
  const chatRef = useRef(null);
  const resizeRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = input;
    setMessages(prev => [...prev, { type: 'user', text: userMessage }]);
    setInput('');
    
    try {
      // Try to get AI response from backend
      const response = await fetch('http://localhost:8001/api/ai/sql/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context: userMessage })
      });
      
      if (response.ok) {
        const aiData = await response.json();
        setMessages(prev => [...prev, { 
          type: 'bot', 
          text: aiData.explanation || aiData.suggestion || 'I can help you optimize your ATOM Cloud infrastructure.'
        }]);
      } else {
        throw new Error('Backend not available');
      }
    } catch (error) {
      // Fallback to simulation responses
      setTimeout(() => {
        const responses = [
          'I\'ve analyzed your Mobile Backend project and found a 23% performance improvement opportunity. Would you like me to enable neural optimization?',
          'Your quantum-safe encryption is ready for deployment. I can help you upgrade to post-quantum cryptography.',
          'I detected potential cost savings of 31% across your projects. Shall I apply the optimization recommendations?',
          'Based on your usage patterns, I suggest enabling auto-scaling for your Analytics Dashboard. Want me to configure it?'
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        setMessages(prev => [...prev, { 
          type: 'bot', 
          text: randomResponse + ' (Simulation mode - backend not available)'
        }]);
      }, 1000);
    }
  };

  const handleMouseDown = (e) => {
    setIsResizing(true);
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = dimensions.width;
    const startHeight = dimensions.height;

    const handleMouseMove = (e) => {
      const newWidth = Math.max(280, startWidth + (startX - e.clientX));
      const newHeight = Math.max(300, startHeight + (startY - e.clientY));
      setDimensions({ width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-16 h-16 bg-white border-2 border-gray-200 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group hover:border-teal-500"
        >
          <Image
            src="/atom-favicon.svg"
            alt="ATOM AI"
            width={36}
            height={36}
            className="group-hover:scale-110 transition-transform filter brightness-0 saturate-100"
            style={{ filter: 'invert(0%) sepia(100%) saturate(7500%) hue-rotate(180deg) brightness(100%) contrast(100%)' }}
          />
        </button>
      </div>

      {/* Chat Panel */}
      {isOpen && (
        <div 
          ref={chatRef}
          className="fixed bottom-24 right-6 bg-card border border-border rounded-lg shadow-xl z-50 flex flex-col select-none"
          style={{ width: dimensions.width, height: dimensions.height }}
        >
          {/* Resize Handle */}
          <div
            ref={resizeRef}
            onMouseDown={handleMouseDown}
            className="absolute -top-1 -left-1 w-4 h-4 cursor-nw-resize bg-primary/20 hover:bg-primary/40 rounded-tl-lg transition-colors"
            title="Drag to resize"
          />
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-r from-teal-500 to-violet-500 rounded-full flex items-center justify-center">
                <Image
                  src="/atom-favicon.svg"
                  alt="ATOM AI"
                  width={20}
                  height={20}
                  className="filter brightness-0 invert"
                />
              </div>
              <div>
                <h3 className="font-semibold">Ask ATOM</h3>
                <p className="text-xs text-muted-foreground">Neural AI Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3" style={{ height: dimensions.height - 120 }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg text-sm ${
                    msg.type === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask ATOM anything..."
                className="flex-1 px-3 py-2 text-sm border border-border rounded-md bg-background"
              />
              <button
                onClick={handleSend}
                className="px-4 py-2 bg-gradient-to-r from-teal-500 to-violet-500 text-white rounded-md text-sm hover:opacity-90"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}