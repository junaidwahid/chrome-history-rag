import { useState } from 'react';

export default function RAGInterface() {
  const [query, setQuery] = useState('');
  const [k, setK] = useState(3);
  const [loading, setLoading] = useState(false);
  const [ragResponse, setRagResponse] = useState(null);
  const [openAIResponse, setOpenAIResponse] = useState(null);
  const [history, setHistory] = useState([]);

  const searchAPI = async (mode) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          mode,
          k,
        }),
      });

      const data = await response.json();
      console.log('Search Results:', data);  // Logs the response data to the terminal

      
      if (mode === 'rag') {
        setRagResponse(data);
      } else {
        setOpenAIResponse(data);
      }

      setHistory(prev => [
        { query, timestamp: new Date().toLocaleString() },
        ...prev.slice(0, 4)
      ]);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#2563eb', marginBottom: '10px' }}>
        RAG based Chrome History Query Search System
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#666' }}>
          Chrome History RAG: Integrated OpenAI GPT with search in indexed Chrome history for smarter, context-aware query responses.        </p>
      </div>

      {/* Search Section */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '20px', 
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
          />
          <button
            onClick={() => searchAPI('rag')}
            disabled={loading || !query}
            style={{
              padding: '10px 20px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Search Index
          </button>
          <button
            onClick={() => searchAPI('generate')}
            disabled={loading || !query}
            style={{
              padding: '10px 20px',
              backgroundColor: '#16a34a',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Ask OpenAI
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Main Content */}
        <div>
          {/* RAG Results */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <h2 style={{ fontSize: '1.5rem', color: '#2563eb', marginBottom: '20px' }}>
              Index Search Results
            </h2>
            
            {loading && query ? (
              <div>Loading...</div>
            ) : ragResponse ? (
              <div>
                <div style={{ marginBottom: '10px', fontSize: '0.9rem', color: '#666' }}>
                  Processing Time: {ragResponse.latency}
                </div>
                <div>{ragResponse.response}</div>
                
                {ragResponse.sources?.map((source, idx) => (
                  <div key={idx} style={{ 
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    padding: '15px',
                    marginTop: '15px'
                  }}>
                    <h3 style={{ marginBottom: '10px' }}>Source {idx + 1}</h3>
                    <p><strong>Title:</strong> {source.title}</p>
                    <p><strong>Description:</strong> {source.description}</p>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          {/* OpenAI Results */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ fontSize: '1.5rem', color: '#16a34a', marginBottom: '20px' }}>
              OpenAI Direct Response
            </h2>
            
            {loading && query ? (
              <div>Loading...</div>
            ) : openAIResponse ? (
              <div>
                <div style={{ marginBottom: '10px', fontSize: '0.9rem', color: '#666' }}>
                  <p>Model: {openAIResponse.model}</p>
                  <p>Processing Time: {openAIResponse.latency}</p>
                </div>
                <div>{openAIResponse.response}</div>
              </div>
            ) : null}
          </div>
        </div>

        {/* Sidebar */}
        <div>
          {/* Settings */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '15px' }}>Settings</h3>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              Number of results (k)
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={k}
              onChange={(e) => setK(parseInt(e.target.value))}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ddd'
              }}
            />
          </div>

          {/* History */}
          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '15px' }}>Recent Queries</h3>
            {history.map((item, idx) => (
              <div key={idx} style={{
                padding: '10px',
                backgroundColor: '#f9fafb',
                borderRadius: '4px',
                marginBottom: '10px'
              }}>
                <div style={{ fontWeight: 500 }}>{item.query}</div>
                <div style={{ fontSize: '0.9rem', color: '#666' }}>{item.timestamp}</div>
              </div>
            ))}
            {history.length === 0 && (
              <div style={{ color: '#666', textAlign: 'center' }}>
                No recent queries
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}