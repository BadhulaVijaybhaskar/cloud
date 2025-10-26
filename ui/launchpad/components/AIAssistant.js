import { useState } from 'react';

export default function AIAssistant({ suggestions }) {
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      content: 'Hello! I\'m ATOM AI, your autonomous cloud assistant. I can help optimize your infrastructure, detect security threats, and suggest improvements.',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'Critical': return 'from-red-500 to-red-600';
      case 'High': return 'from-orange-500 to-orange-600';
      case 'Medium': return 'from-amber-500 to-amber-600';
      case 'Low': return 'from-blue-500 to-blue-600';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'performance': return '⚡';
      case 'security': return '🛡️';
      case 'cost': return '💰';
      case 'scaling': return '📈';
      default: return '🤖';
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        type: 'ai',
        content: 'I\'m analyzing your request using neural networks. This is a simulation - in production, I would provide real-time insights and optimizations.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="space-y-6">
      {/* AI Assistant Header */}
      <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold leading-none tracking-tight flex items-center gap-2">
              💡 AI Recommendations
            </h3>
            <button
              onClick={() => setChatOpen(!chatOpen)}
              className={`p-2 rounded-lg transition-all ${chatOpen ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'}`}
            >
              💬
            </button>
          </div>
          <p className="text-sm text-muted-foreground">Neural analysis insights</p>
        </div>

        {/* Chat Interface */}
        {chatOpen && (
          <div className="border-t border-border/50 p-4">
            <div className="h-64 overflow-y-auto space-y-3 mb-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-lg text-sm ${
                    message.type === 'user' 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-accent text-accent-foreground'
                  }`}>
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask ATOM AI anything..."
                className="flex-1 px-3 py-2 border border-border/50 rounded-lg bg-background/50 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
              <button
                onClick={handleSendMessage}
                className="px-4 py-2 bg-gradient-to-r from-teal-500 to-violet-500 text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                Send
              </button>
            </div>
          </div>
        )}
      </div>

      {/* AI Suggestions */}
      <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6">
          <h3 className="text-xl font-semibold leading-none tracking-tight flex items-center gap-2">
            💡 AI Recommendations
          </h3>
          <p className="text-sm text-muted-foreground">Neural analysis insights</p>
        </div>
        <div className="p-6 pt-0 space-y-4">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="border border-border/50 rounded-lg p-4 hover:bg-accent/20 transition-colors">
              <div className="flex items-start gap-3">
                <div className="text-2xl">{getTypeIcon(suggestion.type)}</div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-sm">{suggestion.title}</h4>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getImpactColor(suggestion.impact)} text-white`}>
                      {suggestion.impact}
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">{suggestion.description}</p>
                  <div className="flex items-center justify-between">
                    <button className="text-xs text-primary hover:text-primary/80 font-medium">
                      {suggestion.action}
                    </button>
                    <div className="text-xs text-muted-foreground">
                      {suggestion.confidence}% confidence
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Neural Network Status */}
      <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6">
          <h3 className="text-xl font-semibold leading-none tracking-tight flex items-center gap-2">
            🧠 Neural Status
          </h3>
        </div>
        <div className="p-6 pt-0 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Learning Engine</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-xs text-emerald-600">Active</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Optimization AI</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-violet-500 rounded-full animate-pulse" />
              <span className="text-xs text-violet-600">Processing</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Threat Detection</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse" />
              <span className="text-xs text-teal-600">Monitoring</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Quantum Encryption</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
              <span className="text-xs text-orange-600">Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-lg border bg-card/80 backdrop-blur-lg border-border/50 text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6">
          <h3 className="text-xl font-semibold leading-none tracking-tight">
            ⚡ Quick Actions
          </h3>
        </div>
        <div className="p-6 pt-0 space-y-2">
          <button className="w-full text-left p-3 rounded-lg hover:bg-accent/50 transition-colors text-sm flex items-center gap-3">
            <span>🔍</span>
            <span>Run Security Scan</span>
          </button>
          <button className="w-full text-left p-3 rounded-lg hover:bg-accent/50 transition-colors text-sm flex items-center gap-3">
            <span>📊</span>
            <span>Performance Analysis</span>
          </button>
          <button className="w-full text-left p-3 rounded-lg hover:bg-accent/50 transition-colors text-sm flex items-center gap-3">
            <span>🤖</span>
            <span>Enable Auto-Optimization</span>
          </button>
          <button className="w-full text-left p-3 rounded-lg hover:bg-accent/50 transition-colors text-sm flex items-center gap-3">
            <span>🛡️</span>
            <span>Activate Quantum Shield</span>
          </button>
        </div>
      </div>
    </div>
  );
}