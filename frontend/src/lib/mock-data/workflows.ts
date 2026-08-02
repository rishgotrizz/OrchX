export const mockWorkflow = {
  id: 'wf-1',
  name: 'Data Extraction Pipeline',
  nodes: [
    { id: '1', type: 'trigger', status: 'completed' },
    { id: '2', type: 'llm', status: 'processing' },
    { id: '3', type: 'database', status: 'pending' }
  ]
};
