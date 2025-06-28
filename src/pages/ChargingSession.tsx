import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  CircularProgress,
  Card,
  CardContent,
  Divider,
  Alert,
  AlertTitle,
  LinearProgress,
  Chip,
} from '@mui/material';
import {
  SearchOutlined,
  EvStationOutlined,
  PaymentOutlined,
  BatteryChargingFullOutlined,
  CheckCircleOutlined,
  RestartAltOutlined,
} from '@mui/icons-material';
import axios from 'axios';

// Types
interface ChargingStation {
  id: string;
  name: string;
  location: string;
  available: boolean;
  rate_kwh: number;
  rate_crypto: number;
  power_kw: number;
}

interface ChargingSessionData {
  id: string;
  session_id: string;
  stationId: string;
  stationName: string;
  status: 'awaiting_payment' | 'charging' | 'completed' | 'error';
  currentEnergy: number;
  kwh_delivered: number;
  kwh_total: number;
  currentAmount: number;
  time_elapsed: number;
  payment?: {
    amount: number;
    currency: string;
    recipient_address: string;
    chain: string;
  };
}

interface PaymentResponse {
  status: string;
  tx_hash: string;
}

const ChargingSession: React.FC = () => {
  // Steps for the charging process
  const steps = ['Find Station', 'Initiate Charging', 'Payment', 'Charging'];
  
  // State
  const [activeStep, setActiveStep] = useState(0);
  const [stations, setStations] = useState<ChargingStation[]>([]);
  const [selectedStation, setSelectedStation] = useState<ChargingStation | null>(null);
  const [session, setSession] = useState<ChargingSessionData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState<boolean>(false);
  const [paymentTx, setPaymentTx] = useState<string | null>(null);
  const [userWalletAddress, setUserWalletAddress] = useState<string | null>("0x123456789abcdef123456789abcdef123456789");
  
  // Get stationId from URL query params
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const stationIdFromUrl = queryParams.get('station');
    // Custom amount for charging (kWh) - Set for a 3-hour charging session
  // Calculate based on an average power rate of 150 kW = 150 * 3 = 450 kWh for 3 hours
  const desiredKwh = 45.0;
  
  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/discover');
        const stationsData = response.data.stations || [];
        setStations(stationsData);
        
        // If station ID is in URL, select it
        if (stationIdFromUrl) {
          const station = stationsData.find((s: ChargingStation) => s.id === stationIdFromUrl);
          if (station) {
            setSelectedStation(station);
            setActiveStep(1); // Move to initiate charging step
          }
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching stations:', err);
        setError('Failed to load charging stations. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStations();
  }, [stationIdFromUrl]);
  // Poll for session status updates when charging
  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    if (session && (session.status === 'charging' || session.status === 'awaiting_payment')) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get('/api/session/current');
          setSession(response.data);
          
          // If charging completed, move to final step
          if (response.data.status === 'completed') {
            setActiveStep(steps.length);
            clearInterval(intervalId);
          }
        } catch (err) {
          console.error('Error polling session status:', err);
        }
      }, 2000); // Poll every 2 seconds
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [session, steps.length]);
  
  // Auto-process payment for better demo experience
  useEffect(() => {
    // If we're in the payment step and have a session, automatically process payment after a short delay
    if (activeStep === 2 && session && !paymentSuccess && !loading) {
      const paymentTimer = setTimeout(() => {
        processPayment();
      }, 2000); // Wait 2 seconds before auto-processing payment
      
      return () => clearTimeout(paymentTimer);
    }
  }, [activeStep, session, paymentSuccess, loading]);
  
  const selectStation = (station: ChargingStation) => {
    setSelectedStation(station);
    setActiveStep(1); // Move to initiate charging step
  };
    const initiateCharging = async () => {
    if (!selectedStation) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('/api/session/start', {
        stationId: selectedStation.id,
        amount: desiredKwh,
        wallet_address: userWalletAddress || undefined
      });
      
      setSession(response.data);
      setActiveStep(2); // Move to payment step
      
      // If status is already charging (e.g. for credit card), move to charging step
      if (response.data.status === 'charging') {
        setActiveStep(3);
      }
      
    } catch (err) {
      console.error('Error initiating charging:', err);
      setError('Failed to start charging session. Please try again.');
    } finally {
      setLoading(false);
    }
  };
    const processPayment = async () => {
    if (!session) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would use the x402 client
      // For demo purposes, we'll simulate the payment proof
      const mockProof = {
        signature: "0x" + Math.random().toString(16).substring(2, 34),
        tx_hash: "0x" + Math.random().toString(16).substring(2, 66),
        amount: session.payment?.amount,
        token: session.payment?.currency || "USDC"
      };
      
      // Call our payment verification endpoint
      const response = await axios.post('/api/payment/verify', {
        proof: mockProof,
        session_id: session.session_id
      });
      
      if (response.data.verified) {
        setPaymentSuccess(true);
        setPaymentTx(response.data.tx_hash);
        setActiveStep(3); // Move to charging step
        
        // Refresh session data to get updated status
        setSession(response.data.session);
      } else {
        setError(`Payment failed: ${response.data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error processing payment:', err);
      setError('Failed to process payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const resetSession = () => {
    setActiveStep(0);
    setSelectedStation(null);
    setSession(null);
    setPaymentSuccess(false);
    setPaymentTx(null);
    setError(null);
  };
  
  // Calculate charging progress percentage
  const getChargingProgress = (): number => {
    if (!session) return 0;
    return Math.min((session.kwh_delivered / session.kwh_total) * 100, 100);
  };
  
  // Format seconds as mm:ss
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Render content based on current step
  const renderStepContent = () => {
    switch (activeStep) {
      case 0: // Find Station
        return (
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>Select a Charging Station</Typography>
            
            {loading ? (
              <Box display="flex" justifyContent="center" my={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Box>
                {stations.map((station) => (
                  <Card 
                    key={station.id} 
                    sx={{ 
                      mb: 2, 
                      cursor: station.available ? 'pointer' : 'not-allowed',
                      opacity: station.available ? 1 : 0.6,
                      border: selectedStation?.id === station.id ? '2px solid' : 'none',
                      borderColor: 'primary.main',
                    }}
                    onClick={() => station.available && selectStation(station)}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="h6">{station.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {station.location}
                          </Typography>
                          <Box mt={1}>
                            <Chip 
                              label={station.available ? 'Available' : 'In Use'} 
                              color={station.available ? 'success' : 'default'}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Chip 
                              label={`${station.power_kw} kW`}
                              color="primary"
                              size="small"
                              sx={{ mr: 1 }}
                            />
                          </Box>
                        </Box>                        <Box textAlign="right">
                          <Typography variant="body2">
                            <strong>USDC:</strong> ${station.rate_crypto}/kWh
                          </Typography>
                          <Typography variant="body2">
                            <strong>Fiat:</strong> ₹{station.rate_kwh}/kWh
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
                
                {stations.length === 0 && !loading && (
                  <Typography color="text.secondary" align="center">
                    No charging stations found.
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        );
        
      case 1: // Initiate Charging
        return (
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>Confirm Charging Details</Typography>
            
            {selectedStation && (
              <Card>
                <CardContent>
                  <Typography variant="h6">{selectedStation.name}</Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {selectedStation.location}
                  </Typography>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body1">Charging Amount:</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {desiredKwh} kWh
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body1">Power Rate:</Typography>
                    <Typography variant="body1">
                      {selectedStation.power_kw} kW
                    </Typography>
                  </Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body1">Crypto Price:</Typography>
                    <Typography variant="body1" fontWeight="bold">
                      ${(selectedStation.rate_crypto * desiredKwh).toFixed(2)} USDC
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body1">Fiat Price:</Typography>
                    <Typography variant="body1">
                      ₹{(selectedStation.rate_kwh * desiredKwh).toFixed(2)}
                    </Typography>
                  </Box>
                  
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body1">Estimated Time:</Typography>
                    <Typography variant="body1">
                      ~{Math.ceil((desiredKwh / selectedStation.power_kw) * 60)} minutes
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
          </Box>
        );
        
      case 2: // Payment
        return (
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>Process Payment</Typography>
            
            {session && session.payment && (
              <Card>
                <CardContent>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <AlertTitle>Payment Required</AlertTitle>
                    Please confirm the payment of ${session.payment.amount} USDC from your CDP Wallet
                  </Alert>
                  
                  <Box mb={3}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Payment Details:
                    </Typography>
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body1">Amount:</Typography>
                      <Typography variant="body1" fontWeight="bold">
                        ${session.payment.amount} {session.payment.currency}
                      </Typography>
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body1">Recipient:</Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {`${session.payment.recipient_address.substring(0, 6)}...${
                          session.payment.recipient_address.substring(
                            session.payment.recipient_address.length - 4
                          )
                        }`}
                      </Typography>
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body1">Network:</Typography>
                      <Typography variant="body1">
                        {session.payment.chain}
                      </Typography>
                    </Box>
                  </Box>
                  
                  {paymentSuccess && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      <AlertTitle>Payment Successful</AlertTitle>
                      Transaction hash: {paymentTx && `${paymentTx.substring(0, 6)}...${paymentTx.substring(paymentTx.length - 4)}`}
                    </Alert>
                  )}
                  
                  {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <AlertTitle>Error</AlertTitle>
                      {error}
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}
          </Box>
        );
        
      case 3: // Charging
        return (
          <Box mt={4}>
            <Typography variant="h6" gutterBottom>Charging in Progress</Typography>
            
            {session && (
              <Card>
                <CardContent>
                  <Box mb={3}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Charging Status:
                    </Typography>
                    
                    <Box sx={{ mb: 2 }}>
                      <Box display="flex" justifyContent="space-between" mb={0.5}>
                        <Typography variant="body2">Progress:</Typography>
                        <Typography variant="body2">
                          {Math.round(getChargingProgress())}%
                        </Typography>
                      </Box>
                      <LinearProgress 
                        variant="determinate" 
                        value={getChargingProgress()} 
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body1">Power Delivered:</Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {session.kwh_delivered.toFixed(2)} / {session.kwh_total.toFixed(2)} kWh
                      </Typography>
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body1">Elapsed Time:</Typography>
                      <Typography variant="body1">
                        {formatTime(session.time_elapsed)}
                      </Typography>
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between">
                      <Typography variant="body1">Status:</Typography>
                      <Chip 
                        label={session.status.replace('_', ' ')} 
                        color={
                          session.status === 'charging' 
                            ? 'primary' 
                            : session.status === 'completed'
                              ? 'success'
                              : 'default'
                        }
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  {session.status === 'charging' && (
                    <Alert severity="info">
                      <AlertTitle>Charging in Progress</AlertTitle>
                      Please wait until charging is complete. You can leave this page and come back later to check the status.
                    </Alert>
                  )}
                  
                  {session.status === 'completed' && (
                    <Alert severity="success">
                      <AlertTitle>Charging Complete</AlertTitle>
                      You have successfully charged {session.kwh_delivered.toFixed(2)} kWh. Thank you for using ChargeX!
                    </Alert>
                  )}
                </CardContent>
              </Card>
            )}
          </Box>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <Box sx={{ mt: 8 }}>
      <Typography variant="h4" component="h1" fontWeight="500" gutterBottom>
        Charging Session
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel
                StepIconProps={{
                  icon: index === 0 ? (
                    <SearchOutlined />
                  ) : index === 1 ? (
                    <EvStationOutlined />
                  ) : index === 2 ? (
                    <PaymentOutlined />
                  ) : index === 3 ? (
                    <BatteryChargingFullOutlined />
                  ) : (
                    <CheckCircleOutlined />
                  ),
                }}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {/* Step Content */}
        {renderStepContent()}
        
        {/* Error Display */}
        {error && activeStep !== 2 && (
          <Alert severity="error" sx={{ mt: 3 }}>
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        )}
        
        {/* Navigation Buttons */}
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            onClick={resetSession}
            startIcon={<RestartAltOutlined />}
            disabled={loading}
          >
            Reset
          </Button>
          
          {activeStep === 0 && (
            <Button
              variant="contained"
              onClick={() => selectedStation && setActiveStep(1)}
              disabled={!selectedStation || loading}
              color="primary"
            >
              Continue
            </Button>
          )}
          
          {activeStep === 1 && (
            <Button
              variant="contained"
              onClick={initiateCharging}
              disabled={!selectedStation || loading}
              color="primary"
            >
              {loading ? <CircularProgress size={24} /> : 'Start Charging'}
            </Button>
          )}
          
          {activeStep === 2 && (
            <Button
              variant="contained"
              onClick={processPayment}
              disabled={!session || loading || paymentSuccess}
              color="primary"
            >
              {loading ? <CircularProgress size={24} /> : 'Pay Now'}
            </Button>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default ChargingSession;
