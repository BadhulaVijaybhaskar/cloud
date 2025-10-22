import { useState, useEffect } from 'react';
import Link from 'next/link';
import Layout from '../components/Layout';
import Card from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setProjects([
        {
          id: '1',
          name: 'E-commerce Platform',
          description: 'Modern online store with payment integration',
          status: 'active',
          created_at: '2024-01-15',
          last_updated: '2024-01-20',
          users: 45,
          storage: '2.1 GB'
        },
        {
          id: '2',
          name: 'Task Management App',
          description: 'Collaborative project management tool',
          status: 'development',
          created_at: '2024-01-10',
          last_updated: '2024-01-19',
          users: 12,
          storage: '850 MB'
        },
        {
          id: '3',
          name: 'Social Media Dashboard',
          description: 'Analytics dashboard for social media metrics',
          status: 'paused',
          created_at: '2024-01-05',
          last_updated: '2024-01-18',
          users: 8,
          storage: '1.2 GB'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'development': return 'bg-blue-100 text-blue-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleCreateProject = async () => {
    try {
      // API call to create project
      const project = {
        id: Date.now().toString(),
        ...newProject,
        status: 'development',
        created_at: new Date().toISOString().split('T')[0],
        last_updated: new Date().toISOString().split('T')[0],
        users: 0,
        storage: '0 MB'
      };
      setProjects([project, ...projects]);
      setShowCreateModal(false);
      setNewProject({ name: '', description: '' });
    } catch (err) {
      alert('Failed to create project');
    }
  };

  return (
    <Layout title="Projects">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Projects</h1>
            <p className="mt-1 text-sm text-gray-500">Manage your development projects</p>
          </div>
          <Button onClick={() => setShowCreateModal(true)} className="mt-4 sm:mt-0">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Project
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="relative flex-1 max-w-md">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search projects..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex space-x-2">
              <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>All Status</option>
                <option>Active</option>
                <option>Development</option>
                <option>Paused</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Projects Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/4"></div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <Card key={project.id} className="hover:shadow-md transition-shadow">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{project.description}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(project.status)}`}>
                      {project.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Users</p>
                      <p className="font-medium">{project.users}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Storage</p>
                      <p className="font-medium">{project.storage}</p>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    <p>Created: {project.created_at}</p>
                    <p>Updated: {project.last_updated}</p>
                  </div>

                  <div className="flex space-x-2 pt-2">
                    <Link href={`/projects/${project.id}`} className="flex-1">
                      <Button variant="secondary" size="sm" className="w-full">
                        View Details
                      </Button>
                    </Link>
                    <Button variant="secondary" size="sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {!loading && filteredProjects.length === 0 && (
          <Card>
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No projects found</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating a new project</p>
              <Button onClick={() => setShowCreateModal(true)} className="mt-4">
                Create Project
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Create Project Modal */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Project">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={newProject.name}
              onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={newProject.description}
              onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Enter project description"
            />
          </div>
          <div className="flex space-x-3 pt-4">
            <Button 
              onClick={handleCreateProject} 
              disabled={!newProject.name.trim()} 
              className="flex-1"
            >
              Create Project
            </Button>
            <Button 
              variant="secondary" 
              onClick={() => setShowCreateModal(false)} 
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
}