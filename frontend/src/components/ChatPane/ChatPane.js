import React, { useState, useRef } from 'react';
import './ChatPane.css';

const ChatPane = ({ onPipelineUpdate }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: inputValue
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Received non-JSON response: ${text.substring(0, 100)}...`);
      }

      const data = await response.json();
      
      if (data.success) {
        // Debug log to see what we're receiving
        console.log('LLM Response:', data);
        
        const assistantMessage = {
          role: 'assistant',
          content: typeof data.response === 'string' ? data.response : JSON.stringify(data.response),
          timestamp: new Date().toISOString()
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Handle pipeline data - check the actual response structure
        let pipelineData = null;
        if (data.response && typeof data.response === 'object') {
          if (data.response.pipeline_flow && data.response.json_configs) {
            pipelineData = data.response;
          } else if (data.response.pipeline_flow || data.response.json_configs) {
            // Partial response, restructure it
            pipelineData = {
              pipeline_flow: data.response.pipeline_flow || { nodes: [], edges: [] },
              json_configs: data.response.json_configs || { linked_services: [], datasets: [], pipeline: {} }
            };
          }
        } else if (typeof data.response === 'string') {
          // Try to parse string response
          try {
            const parsed = JSON.parse(data.response);
            if (parsed.pipeline_flow && parsed.json_configs) {
              pipelineData = parsed;
            }
          } catch (e) {
            console.log('Could not parse string response as JSON');
          }
        }
        
        if (pipelineData) {
          console.log('Sending pipeline data to update:', pipelineData);
          onPipelineUpdate(pipelineData);
        } else {
          console.log('No valid pipeline data found in response');
        }
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-pane">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.role === 'assistant' ? (
                <PipelineResponse content={msg.content} />
              ) : (
                msg.content
              )}
            </div>
            <div className="timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe your data pipeline (e.g., 'Create a pipeline to copy data from SQL Server to Databricks')..."
          disabled={isLoading}
        />
        <button 
          onClick={handleSend} 
          disabled={isLoading || !inputValue.trim()}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

const PipelineResponse = ({ content }) => {
  try {
    // Handle both string and object responses
    let data;
    if (typeof content === 'string') {
      // Try to parse as JSON first
      try {
        data = JSON.parse(content);
      } catch {
        // If not JSON, treat as plain text
        return <div>{content}</div>;
      }
    } else {
      data = content;
    }
    
    return (
      <div className="pipeline-response">
        <p>{data.explanation || data.message || 'Pipeline configuration generated'}</p>
        {(data.json_configs || data.pipeline_flow) && (
          <div className="config-summary">
            <span className="summary-item">
              <strong>Linked Services:</strong> {data.json_configs?.linked_services?.length || 0}
            </span>
            <span className="summary-item">
              <strong>Datasets:</strong> {data.json_configs?.datasets?.length || 0}
            </span>
            <span className="summary-item">
              <strong>Activities:</strong> {data.json_configs?.pipeline?.properties?.activities?.length || 0}
            </span>
          </div>
        )}
      </div>
    );
  } catch (e) {
    // If parsing fails, display as plain text
    return <div>{content}</div>;
  }
};

export default ChatPane;