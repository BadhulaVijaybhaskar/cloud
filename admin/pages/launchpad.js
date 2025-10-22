import { useState } from 'react';
import axios from 'axios';

export default function Launchpad() {
  const [idea, setIdea] = useState('');
  const [results, setResults] = useState([]);

  const handleAnalyze = async () => {
    // Mock analysis - in real app, this would call an API
    setResults([
      { title: 'Research Summary', content: 'AI-powered backend platform' },
      { title: 'Suggested Project Name', content: 'Naksha Cloud MVP' },
      { title: 'Start Project', action: true }
    ]);
  };

  const handleStartProject = async () => {
    try {
      // This would create a workspace and project via GraphQL/REST
      alert('Project started!');
    } catch (err) {
      alert('Failed to start project');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Launchpad</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <textarea
              placeholder="Describe your product idea..."
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              className="w-full h-32 p-4 border rounded"
            />
            <button
              onClick={handleAnalyze}
              className="mt-4 w-full bg-blue-500 text-white p-2 rounded"
            >
              Analyze
            </button>
          </div>
          <div className="md:col-span-2">
            {results.length > 0 && (
              <div className="space-y-4">
                {results.map((result, idx) => (
                  <div key={idx} className="bg-white p-4 rounded shadow">
                    <h3 className="font-bold">{result.title}</h3>
                    <p>{result.content}</p>
                    {result.action && (
                      <button
                        onClick={handleStartProject}
                        className="mt-2 bg-green-500 text-white px-4 py-2 rounded"
                      >
                        Start Project
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
