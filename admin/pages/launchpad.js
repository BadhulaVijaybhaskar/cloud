import { useState } from 'react';
import Layout from '../components/Layout';
import Card from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';

export default function Launchpad() {
  const [idea, setIdea] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [projectName, setProjectName] = useState('');

  const handleAnalyze = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setResults([
        { 
          title: 'Market Research', 
          content: 'Your idea shows strong potential in the SaaS market with similar solutions generating $10M+ ARR.',
          icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'
        },
        { 
          title: 'Technical Stack', 
          content: 'Recommended: React/Next.js frontend, Node.js backend, PostgreSQL database, Redis cache.',
          icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
        },
        { 
          title: 'MVP Features', 
          content: 'Core features: User auth, data management, API endpoints, admin dashboard. Est. 4-6 weeks.',
          icon: 'M13 10V3L4 14h7v7l9-11h-7z'
        }
      ]);
      setLoading(false);
    }, 2000);
  };

  const handleStartProject = () => {
    setShowModal(true);
  };

  const handleCreateProject = async () => {
    try {
      // API call to create project
      console.log('Creating project:', projectName);
      setShowModal(false);
      setProjectName('');
      alert('Project created successfully!');
    } catch (err) {
      alert('Failed to create project');
    }
  };

  return (
    <Layout title="Launchpad">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Project Launchpad</h1>
          <p className="text-xl text-gray-600">Transform your ideas into reality with AI-powered insights</p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <Card title="Describe Your Idea" subtitle="Tell us about your product vision">
              <div className="space-y-4">
                <textarea
                  placeholder="Example: A social media platform for developers to share code snippets and collaborate on projects..."
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                <Button 
                  onClick={handleAnalyze} 
                  loading={loading}
                  disabled={!idea.trim()}
                  className="w-full"
                  size="lg"
                >
                  {loading ? 'Analyzing...' : 'Analyze Idea'}
                </Button>
              </div>
            </Card>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-3">
            {loading && (
              <Card>
                <div className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Analyzing your idea...</p>
                  </div>
                </div>
              </Card>
            )}

            {results.length > 0 && !loading && (
              <div className="space-y-6">
                <div className="grid gap-6">
                  {results.map((result, idx) => (
                    <Card key={idx}>
                      <div className="flex items-start space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={result.icon} />
                            </svg>
                          </div>
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">{result.title}</h3>
                          <p className="text-gray-600">{result.content}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>

                <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-green-200">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Start?</h3>
                    <p className="text-gray-600 mb-6">Create your project and get started with development</p>
                    <Button onClick={handleStartProject} variant="success" size="lg">
                      Create Project
                    </Button>
                  </div>
                </Card>
              </div>
            )}

            {!loading && results.length === 0 && (
              <Card>
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No analysis yet</h3>
                  <p className="mt-1 text-sm text-gray-500">Describe your idea to get AI-powered insights</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Create Project Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create New Project">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name"
            />
          </div>
          <div className="flex space-x-3 pt-4">
            <Button onClick={handleCreateProject} disabled={!projectName.trim()} className="flex-1">
              Create Project
            </Button>
            <Button variant="secondary" onClick={() => setShowModal(false)} className="flex-1">
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}
