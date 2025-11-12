import React from 'react';
import ProjectList from '../components/ProjectList';

export default function ProjectsPage(){
  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Projects</h1>
      <ProjectList />
    </div>
  );
}