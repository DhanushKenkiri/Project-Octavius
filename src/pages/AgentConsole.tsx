import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  IconButton,
  Avatar,
  Tooltip,
  Fade,
  Slide,
  Container,
  Stack,
  Badge,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AgentIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  EvStation as EvStationIcon,
  Payments as PaymentsIcon,
  BatteryChargingFull as BatteryIcon,
  AutoAwesome as SparkleIcon,
  Psychology as BrainIcon,
  ElectricBolt as BoltIcon,
  Lightbulb as IdeaIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface AgentMessage {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: number;
  action?: string;
  response?: any;
}

const AgentConsole: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [messages, setMessages] = useState<AgentMessage[]>([
    {
      id: 'welcome',
      role: 'agent',
      content: '🚗⚡ Welcome to ChargeX Agent! I\'m your AI-powered EV charging assistant. I can help you find stations, monitor charging sessions, process payments, and answer questions about electric vehicle charging. How can I assist you today?',
      timestamp: Date.now(),
    }
  ]);
  const [loading, setLoading] = useState<boolean>(false);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Smart response generator for demo purposes
  const getSmartResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('station') || input.includes('charger') || input.includes('find')) {
      return '🗺️ I found several charging stations near you in Bangalore! There are currently 5 available stations including ChargeX Indiranagar, ChargeX Whitefield Hub, and ChargeX Koramangala. Would you like me to show you the map or start a charging session at a specific location?';
    }
    
    if (input.includes('payment') || input.includes('pay') || input.includes('usdc') || input.includes('wallet')) {
      return '💳 I can help you with crypto payments using your CDP wallet! Your current USDC balance is $75.45 on Base Sepolia testnet. Charging typically costs 0.24-0.29 USDC per kWh. Would you like me to check your payment history or set up a new payment?';
    }
    
    if (input.includes('charge') || input.includes('charging') || input.includes('session')) {
      return '🔋 I can start a 3-hour charging session for you! Based on your location, I recommend ChargeX MG Road (200kW fast charging) or ChargeX Indiranagar (150kW). The estimated cost would be around $11-13 USDC for a full charge. Shall I initiate a session?';
    }
    
    if (input.includes('battery') || input.includes('range') || input.includes('level')) {
      return '⚡ Your Tesla Model 3 is currently at 42% battery with an estimated range of 142 miles. Based on your typical usage, I recommend charging when you reach your next destination. Would you like me to find charging stations along your route?';
    }
    
    if (input.includes('help') || input.includes('what') || input.includes('how')) {
      return '🤖 I\'m ChargeX Agent, your intelligent EV charging companion! I can:\n\n• Find and reserve charging stations\n• Process crypto payments with x402\n• Monitor charging sessions in real-time\n• Provide route planning with charging stops\n• Answer questions about EV charging\n\nJust ask me anything about electric vehicle charging!';
    }
    
    if (input.includes('price') || input.includes('cost') || input.includes('rate')) {
      return '💰 Current charging rates in Bangalore:\n• ChargeX stations: ₹19.5-23.5 per kWh (fiat) or 0.24-0.29 USDC per kWh\n• Fast charging (150-200kW): Premium rates\n• Standard charging (50-100kW): Economy rates\n\nCrypto payments offer 15-20% savings compared to traditional payment methods!';
    }
    
    return '';
  };

  const sendMessage = async () => {
    if (!query.trim() || loading) return;

    const userMessage: AgentMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query.trim(),
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setLoading(true);
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(async () => {
      try {
        // Try to get smart response first
        const smartResponse = getSmartResponse(userMessage.content);
        
        let agentResponse: AgentMessage;
        
        if (smartResponse) {
          // Use smart local response
          agentResponse = {
            id: `agent-${Date.now()}`,
            role: 'agent',
            content: smartResponse,
            timestamp: Date.now(),
          };
        } else {
          // Try API call for more complex queries
          try {
            const response = await axios.post('/api/agent/action', {
              prompt: userMessage.content,
              session_id: sessionId,
            });
            
            agentResponse = {
              id: `agent-${Date.now()}`,
              role: 'agent',
              content: response.data.message || response.data.response || 'I processed your request successfully!',
              timestamp: Date.now(),
              action: response.data.action,
              response: response.data,
            };
            
            if (response.data.session_id) {
              setSessionId(response.data.session_id);
            }
          } catch (error) {
            // Fallback response for API errors
            agentResponse = {
              id: `agent-${Date.now()}`,
              role: 'agent',
              content: '🤖 I\'m currently experiencing some connection issues with my cloud brain. Let me help you with what I know locally! Could you try rephrasing your question about EV charging, stations, or payments?',
              timestamp: Date.now(),
            };
          }
        }
        
        setMessages(prev => [...prev, agentResponse]);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage: AgentMessage = {
          id: `error-${Date.now()}`,
          role: 'agent',
          content: '🤖 I\'m currently experiencing some connection issues with my cloud brain. Let me help you with what I know locally! Could you try rephrasing your question?',
          timestamp: Date.now(),
        };
        
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setLoading(false);
        setIsTyping(false);
      }
    }, 1000 + Math.random() * 1500); // Random delay between 1-2.5 seconds
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome',
        role: 'agent',
        content: '🚗⚡ Welcome back to ChargeX Agent! How can I help you with your EV charging needs today?',
        timestamp: Date.now(),
      }
    ]);
    setSessionId(null);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 8, mb: 4 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 48, height: 48 }}>
          <BrainIcon sx={{ fontSize: 28 }} />
        </Avatar>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="600">
            ChargeX Agent Console
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Your AI-powered EV charging assistant
          </Typography>
        </Box>
        <Box sx={{ ml: 'auto' }}>
          <Tooltip title="Clear conversation">
            <IconButton onClick={clearChat} color="primary">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Agent Status */}
      <Paper 
        sx={{ 
          p: 2, 
          mb: 3, 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 3,
        }}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <Badge color="success" variant="dot">
            <AgentIcon sx={{ fontSize: 32 }} />
          </Badge>
          <Box flex={1}>
            <Typography variant="h6" fontWeight="500">
              Agent Status: Active & Ready
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Connected to ChargeX Network • Base Sepolia Testnet • x402 Payments Ready
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Chip 
              icon={<BoltIcon />} 
              label="AI Powered" 
              size="small" 
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
            <Chip 
              icon={<EvStationIcon />} 
              label="7 Stations" 
              size="small" 
              sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Stack>
        </Stack>
      </Paper>

      {/* Chat Interface */}
      <Paper 
        sx={{ 
          height: 600, 
          display: 'flex', 
          flexDirection: 'column',
          borderRadius: 3,
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        }}
      >
        {/* Messages Area */}
        <Box 
          sx={{ 
            flex: 1, 
            overflow: 'auto', 
            p: 2,
            background: 'linear-gradient(to bottom, #f8f9ff 0%, #ffffff 100%)',
          }}
        >
          {messages.map((message, index) => (
            <Fade key={message.id} in timeout={500}>
              <Box
                sx={{
                  display: 'flex',
                  mb: 2,
                  justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                {message.role === 'agent' && (
                  <Avatar 
                    sx={{ 
                      bgcolor: 'primary.main', 
                      mr: 1, 
                      width: 36, 
                      height: 36 
                    }}
                  >
                    <AgentIcon fontSize="small" />
                  </Avatar>
                )}
                
                <Card
                  sx={{
                    maxWidth: '75%',
                    bgcolor: message.role === 'user' 
                      ? 'primary.main' 
                      : 'background.paper',
                    color: message.role === 'user' ? 'white' : 'text.primary',
                    boxShadow: message.role === 'user' 
                      ? '0 4px 20px rgba(33, 150, 243, 0.3)'
                      : '0 2px 12px rgba(0,0,0,0.1)',
                    borderRadius: message.role === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
                  }}
                >
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Typography 
                      variant="body1" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.5,
                      }}
                    >
                      {message.content}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        opacity: 0.7, 
                        mt: 1, 
                        display: 'block',
                        fontSize: '0.75rem',
                      }}
                    >
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </Typography>
                  </CardContent>
                </Card>

                {message.role === 'user' && (
                  <Avatar 
                    sx={{ 
                      bgcolor: 'secondary.main', 
                      ml: 1, 
                      width: 36, 
                      height: 36 
                    }}
                  >
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Box>
            </Fade>
          ))}
          
          {/* Typing Indicator */}
          {isTyping && (
            <Slide direction="up" in={isTyping}>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar 
                  sx={{ 
                    bgcolor: 'primary.main', 
                    mr: 1, 
                    width: 36, 
                    height: 36 
                  }}
                >
                  <AgentIcon fontSize="small" />
                </Avatar>
                <Card sx={{ p: 2, bgcolor: 'background.paper' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <SparkleIcon sx={{ fontSize: 16, color: 'primary.main' }} />
                    <Typography variant="body2" color="text.secondary">
                      Agent is thinking...
                    </Typography>
                    <CircularProgress size={16} />
                  </Stack>
                </Card>
              </Box>
            </Slide>
          )}
          
          <div ref={messagesEndRef} />
        </Box>
        
        <Divider />
        
        {/* Input Area */}
        <Box 
          sx={{ 
            p: 2, 
            bgcolor: 'background.paper',
            borderTop: '1px solid rgba(0,0,0,0.12)',
          }}
        >
          <Stack direction="row" spacing={1} alignItems="center">
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask me about EV charging, stations, payments, or anything else..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              disabled={loading}
              multiline
              maxRows={3}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  '&:hover fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
            />
            <Tooltip title="Send message">
              <Box>
                <IconButton
                  onClick={sendMessage}
                  disabled={loading || !query.trim()}
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '&:disabled': {
                      bgcolor: 'action.disabled',
                    },
                    width: 48,
                    height: 48,
                  }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
                </IconButton>
              </Box>
            </Tooltip>
          </Stack>
        </Box>
      </Paper>

      {/* Quick Actions */}
      <Paper sx={{ mt: 3, p: 2, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <IdeaIcon sx={{ mr: 1, color: 'warning.main' }} />
          Quick Actions
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Button
            variant="outlined"
            size="small"
            startIcon={<EvStationIcon />}
            onClick={() => setQuery('Find me the nearest charging station')}
            sx={{ borderRadius: 2 }}
          >
            Find Stations
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<BatteryIcon />}
            onClick={() => setQuery('Start a 3-hour charging session')}
            sx={{ borderRadius: 2 }}
          >
            Start Charging
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<PaymentsIcon />}
            onClick={() => setQuery('Check my USDC wallet balance')}
            sx={{ borderRadius: 2 }}
          >
            Check Wallet
          </Button>
          <Button
            variant="outlined"
            size="small"
            startIcon={<BrainIcon />}
            onClick={() => setQuery('How does ChargeX Agent work?')}
            sx={{ borderRadius: 2 }}
          >
            How it Works
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
};

export default AgentConsole;
