import React from 'react';

const MOCK = [
  {id:'p-1', name:'demo-project', region:'us-west1', status:'active'},
  {id:'p-2', name:'test-project', region:'eu-central1', status:'staging'}
];

export default function ProjectList(){
  return (
    <div className="grid gap-4">
      {MOCK.map(p => (
        <div key={p.id} className="bg-white p-4 rounded shadow">
          <div className="font-medium">{p.name}</div>
          <div className="text-sm text-gray-500">{p.region} • {p.status}</div>
        </div>
      ))}
    </div>
  );
}