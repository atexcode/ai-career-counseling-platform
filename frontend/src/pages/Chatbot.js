import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Avatar,
  Paper,
  IconButton,
  Chip
} from '@mui/material';
import {
  Send,
  SmartToy,
  Person,
  Refresh
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const Chatbot = () => {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    if (user && messages.length === 0) {
      setMessages([
        {
          id: 1,
          text: `Hello ${user.name}! I'm your AI career counselor. I can help you with career guidance, skill recommendations, job search advice, and more. What would you like to know?`,
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
    }
  }, [user]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/api/chatbot/message', {
        message: inputMessage,
        context: '',
        conversation_history: messages.slice(-10) // Send last 10 messages for context
      });

      if (response.data.success) {
        const botMessage = {
          id: Date.now() + 1,
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          suggestions: response.data.suggestions || []
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        setError('Failed to get response from chatbot');
      }
    } catch (err) {
      setError('Error communicating with chatbot. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
  };

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        text: `Hello ${user.name}! I'm your AI career counselor. How can I help you today?`,
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
  };

  const quickQuestions = [
    "What career paths suit my skills?",
    "How can I improve my resume?",
    "What skills are in high demand?",
    "How do I prepare for interviews?",
    "What's the job market like in my field?"
  ];

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Career Counselor
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Chat with our AI counselor for personalized career guidance and advice.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Chat Interface */}
        <Card sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
          {/* Chat Header */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                <SmartToy />
              </Avatar>
              <Box>
                <Typography variant="h6">AI Career Counselor</Typography>
                <Typography variant="body2" color="text.secondary">
                  Online • Ready to help
                </Typography>
              </Box>
            </Box>
            <IconButton onClick={clearChat} size="small">
              <Refresh />
            </IconButton>
          </Box>

          {/* Messages */}
          <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            {messages.map((message) => (
              <Box
                key={message.id}
                sx={{
                  display: 'flex',
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    maxWidth: '70%',
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row'
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.sender === 'user' ? 'secondary.main' : 'primary.main',
                      width: 32,
                      height: 32,
                      mx: 1
                    }}
                  >
                    {message.sender === 'user' ? <Person /> : <SmartToy />}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                      color: message.sender === 'user' ? 'white' : 'text.primary',
                      borderRadius: 2
                    }}
                  >
                    {message.sender === 'bot' ? (
                      <Box
                        sx={{
                          '& p': {
                            margin: '0.5em 0',
                            '&:first-of-type': { marginTop: 0 },
                            '&:last-of-type': { marginBottom: 0 }
                          },
                          '& ul, & ol': {
                            margin: '0.5em 0',
                            paddingLeft: '1.5em'
                          },
                          '& li': {
                            margin: '0.25em 0'
                          },
                          '& h1, & h2, & h3, & h4, & h5, & h6': {
                            margin: '0.5em 0 0.25em 0',
                            fontWeight: 600,
                            '&:first-of-type': { marginTop: 0 }
                          },
                          '& code': {
                            backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
                            padding: '0.2em 0.4em',
                            borderRadius: '3px',
                            fontSize: '0.9em',
                            fontFamily: 'monospace'
                          },
                          '& pre': {
                            backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
                            padding: '1em',
                            borderRadius: '4px',
                            overflow: 'auto',
                            '& code': {
                              backgroundColor: 'transparent',
                              padding: 0
                            }
                          },
                          '& blockquote': {
                            borderLeft: `3px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.3)'}`,
                            paddingLeft: '1em',
                            margin: '0.5em 0',
                            fontStyle: 'italic'
                          },
                          '& a': {
                            color: message.sender === 'user' ? '#fff' : 'primary.main',
                            textDecoration: 'underline'
                          },
                          '& strong': {
                            fontWeight: 600
                          },
                          '& em': {
                            fontStyle: 'italic'
                          },
                          '& table': {
                            borderCollapse: 'collapse',
                            width: '100%',
                            margin: '0.5em 0'
                          },
                          '& th, & td': {
                            border: `1px solid ${message.sender === 'user' ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)'}`,
                            padding: '0.5em',
                            textAlign: 'left'
                          },
                          '& th': {
                            fontWeight: 600,
                            backgroundColor: message.sender === 'user' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'
                          }
                        }}
                      >
                        <ReactMarkdown>{message.text}</ReactMarkdown>
                      </Box>
                    ) : (
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {message.text}
                      </Typography>
                    )}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        {message.suggestions.map((suggestion, index) => (
                          <Chip
                            key={index}
                            label={suggestion}
                            size="small"
                            onClick={() => handleSuggestionClick(suggestion)}
                            sx={{ mr: 1, mb: 1, cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    )}
                    <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mt: 1 }}>
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </Paper>
                </Box>
              </Box>
            ))}
            
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
                    <SmartToy />
                  </Avatar>
                  <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <CircularProgress size={20} />
                  </Paper>
                </Box>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>

          {/* Quick Questions */}
          {messages.length <= 1 && (
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>
                Quick Questions:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {quickQuestions.map((question, index) => (
                  <Chip
                    key={index}
                    label={question}
                    size="small"
                    onClick={() => handleSuggestionClick(question)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Input */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                multiline
                maxRows={3}
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
              />
              <Button
                variant="contained"
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                sx={{ minWidth: 'auto', px: 2 }}
              >
                <Send />
              </Button>
            </Box>
          </Box>
        </Card>

        {/* Tips */}
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Tips for Better Conversations
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Be specific about your career goals and current situation<br/>
              • Ask about specific skills, industries, or job roles<br/>
              • Request personalized advice based on your profile<br/>
              • Ask for resume tips, interview preparation, or networking advice
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Chatbot;