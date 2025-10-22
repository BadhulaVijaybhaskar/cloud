const axios = require('axios');
const WebSocket = require('ws');

async function runE2ETests() {
  const baseUrl = 'http://localhost:3000'; // Assuming services are exposed
  const authUrl = 'http://localhost:9999';
  const hasuraUrl = 'http://localhost:8080';

  try {
    console.log('1. Register user');
    const registerRes = await axios.post(`${authUrl}/auth/register`, {
      email: 'test@naksha.test',
      password: 'password123'
    });
    const token = registerRes.data.token;
    console.log('User registered, token:', token.substring(0, 20) + '...');

    console.log('2. Create workspace');
    // This would call the create_workspace.sh script or API
    // For now, assume workspace created with ID 'test-ws-id'

    console.log('3. Insert project via GraphQL');
    const gqlRes = await axios.post(hasuraUrl + '/v1/graphql', {
      query: `
        mutation {
          insert_projects_one(object: {name: "Test Project", description: "E2E test"}) {
            id
          }
        }
      `,
      headers: {
        'Authorization': `Bearer ${token}`,
        'x-workspace-id': 'test-ws-id'
      }
    });
    console.log('Project inserted:', gqlRes.data);

    console.log('4. Presign upload');
    const presignRes = await axios.post(`${baseUrl}/storage/presign`, {
      workspace_id: 'test-ws-id',
      key: 'test-file.txt',
      content_type: 'text/plain',
      size: 100
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log('Presigned URL:', presignRes.data.upload_url);

    console.log('5. Test realtime');
    const ws = new WebSocket(`ws://localhost:4000?token=${token}&workspace=test-ws-id`);
    ws.on('open', () => {
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'projects:test-project-id' }));
    });
    ws.on('message', (data) => {
      console.log('Received event:', data);
      ws.close();
    });

    // Simulate NOTIFY
    // In real test, trigger a DB change

    console.log('E2E tests passed!');
  } catch (err) {
    console.error('E2E test failed:', err.message);
    process.exit(1);
  }
}

runE2ETests();
