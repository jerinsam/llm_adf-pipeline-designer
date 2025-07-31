import React, { useState } from 'react';
import ChatPane from './components/ChatPane';
import PipelineFlow from './components/PipelineFlow';
import Header from './components/Header';
import './App.css';

function App() {
  const [pipelineData, setPipelineData] = useState(null);
  const [backendError, setBackendError] = useState(null);

  const handlePipelineUpdate = (data) => {
    console.log('App received pipeline data:', data); // Debug log
    setPipelineData(data);
    setBackendError(null);
  };

  const handleRetryConnection = async () => {
    setBackendError(null);
  };

  return (
    <div className="app-container">
      <Header />
      {backendError && (
        <div className="error-banner">
          <p>{backendError}</p>
          <button onClick={handleRetryConnection} className="retry-button">
            Dismiss
          </button>
        </div>
      )}
      <div className="main-content">
        <div className="left-pane">
          <ChatPane 
            onPipelineUpdate={handlePipelineUpdate}
          />
        </div>
        <div className="right-pane">
          <PipelineFlow pipelineData={pipelineData} />
        </div>
      </div>
    </div>
  );
}

export default App;