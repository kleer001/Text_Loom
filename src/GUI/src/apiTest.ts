// Simple API connectivity test

import { apiClient } from './apiClient';

async function testApiConnection() {
  console.log('🔍 Testing API connection...');
  
  try {
    // Test 1: Health check
    console.log('\n1. Health Check');
    const health = await apiClient.healthCheck();
    console.log('✅ Health:', health);
    
    // Test 2: Load workspace
    console.log('\n2. Load Workspace');
    const workspace = await apiClient.getWorkspace();
    console.log(`✅ Workspace loaded successfully!`);
    console.log(`   - Nodes: ${workspace.nodes.length}`);
    console.log(`   - Connections: ${workspace.connections.length}`);
    console.log(`   - Globals: ${Object.keys(workspace.globals).length}`);
    
    if (workspace.nodes.length > 0) {
      console.log('\n📦 Sample Node:');
      const firstNode = workspace.nodes[0];
      console.log(`   - Name: ${firstNode.name}`);
      console.log(`   - Type: ${firstNode.type}`);
      console.log(`   - Path: ${firstNode.path}`);
      console.log(`   - State: ${firstNode.state}`);
      console.log(`   - Parameters: ${Object.keys(firstNode.parameters).length}`);
    }
    
    if (workspace.connections.length > 0) {
      console.log('\n🔗 Sample Connection:');
      const firstConn = workspace.connections[0];
      console.log(`   - Source: ${firstConn.source_node_path}[${firstConn.source_output_index}]`);
      console.log(`   - Target: ${firstConn.target_node_path}[${firstConn.target_input_index}]`);
    }
    
    console.log('\n✨ All tests passed!');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    console.error('\n💡 Make sure the backend is running:');
    console.error('   uvicorn api.main:app --reload');
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testApiConnection();
}

export { testApiConnection };
