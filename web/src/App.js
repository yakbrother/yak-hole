import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef(null);

  // Check backend connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await axios.get(`${API_BASE_URL}/health`);
        setConnected(true);
      } catch (error) {
        setConnected(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConversations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/conversations/${conversationId}`);
      setCurrentConversation(conversationId);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    // Add user message to chat
    const newUserMessage = {
      type: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Send to backend
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: userMessage,
        conversation_id: currentConversation
      });

      // Add bot response to chat
      const botMessage = {
        type: 'bot',
        content: response.data.response,
        sources: response.data.sources || [],
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Update current conversation ID
      if (response.data.conversation_id) {
        setCurrentConversation(response.data.conversation_id);
        loadConversations(); // Refresh conversation list
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage = {
        type: 'bot',
        content: 'Sorry, there was an error processing your message. Please make sure the backend is running and try again.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🕳️ Yak Hole</h1>
        <div className="status">
          <div className={`status-dot ${connected ? '' : 'offline'}`} 
               style={{ background: connected ? '#4caf50' : '#f44336' }}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </header>

      <main className="main">
        <aside className="sidebar">
          <div className="sidebar-header">
            <h3>Conversations</h3>
            <button 
              onClick={startNewConversation}
              style={{
                marginTop: '0.5rem',
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '6px',
                background: '#4caf50',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              New Chat
            </button>
          </div>
          
          <div className="conversations">
            {conversations.map((conv) => (
              <div 
                key={conv.id}
                className={`conversation-item ${conv.id === currentConversation ? 'active' : ''}`}
                onClick={() => loadConversation(conv.id)}
              >
                <div className="conversation-preview">
                  {conv.preview || 'New conversation'}
                </div>
                <div className="conversation-time">
                  {new Date(conv.updated_at || conv.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </aside>

        <div className="chat-area">
          <div className="messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div>
                  <h2>Welcome to Yak Hole</h2>
                  <p>Ask me anything about your notes!</p>
                  <p style={{ fontSize: '0.9rem', color: '#666' }}>
                    Make sure you've processed your notes using:<br />
                    <code>python3 backend/ingest_notes.py --notes-dir /path/to/your/notes</code>
                  </p>
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                  <div>{message.content}</div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="sources">
                      <div className="sources-title">Sources:</div>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="source-item">
                          📄 {source.filename || source.title || 'Unknown source'}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
            
            {loading && (
              <div className="message loading">
                <div>Thinking...</div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={connected ? "Ask about your notes..." : "Backend not connected"}
              disabled={!connected || loading}
            />
            <button 
              onClick={sendMessage}
              disabled={!connected || loading || !inputMessage.trim()}
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;