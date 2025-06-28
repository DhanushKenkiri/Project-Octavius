import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Chip,
  CircularProgress,
  Tooltip,
  Paper,
  Avatar,
  Stack,
} from '@mui/material';
import {
  BatteryChargingFull as BatteryIcon,
  AccountBalanceWallet as WalletIcon,
  Bolt as BoltIcon,
  EvStation as EvStationIcon,
  History as HistoryIcon,
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

interface PaymentRecord {
  amount: number;
  currency: string;
  timestamp: number;
  tx_hash: string;
  session_id: string;
}

const Dashboard: React.FC = () => {
  const [stations, setStations] = useState<ChargingStation[]>([]);
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Mock battery and wallet data
  const batteryLevel = 42;
  const usdcBalance = 75.45;
  const estimatedRange = 142;
  const activeSessions = 0;

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch stations and payment data in parallel
        const [stationsResponse, paymentsResponse] = await Promise.all([
          axios.get('/api/discover'),
          axios.get('/api/payments')
        ]);
        
        setStations(stationsResponse.data.stations || []);
        setPayments(paymentsResponse.data.payments || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  const getRecentPayments = () => {
    return payments.slice(0, 3);
  };

  return (
    <Box sx={{ mt: 8 }}>
      <Typography variant="h4" component="h1" fontWeight="500" gutterBottom>
        Dashboard
      </Typography>
      
      {loading ? (
        <Box display="flex" justifyContent="center" my={6}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box my={4}>
          <Typography color="error">{error}</Typography>
          <Button 
            variant="contained" 
            color="primary" 
            sx={{ mt: 2 }}
            onClick={() => window.location.reload()}
          >
            Retry
          </Button>
        </Box>
      ) : (
        <>
          {/* Vehicle Status */}
          <Paper
            sx={{
              p: 3,
              mb: 4,
              borderRadius: 2,
              background: 'linear-gradient(90deg, #2c3e50 0%, #4c4c4c 100%)',
            }}
          >
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box display="flex" alignItems="center">
                  <Avatar
                    sx={{
                      width: 56,
                      height: 56,
                      bgcolor: 'primary.main',
                      mr: 2,
                    }}
                  >
                    <BatteryIcon sx={{ fontSize: 32 }} />
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="500">Vehicle Status</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tesla Model 3
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Tooltip title="Current battery level">
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Battery
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {batteryLevel}%
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Tooltip title="Estimated range">
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Range
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {estimatedRange} mi
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Tooltip title="USDC balance in CDP wallet">
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          USDC Balance
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          ${usdcBalance}
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Tooltip title="Active charging sessions">
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Active Sessions
                        </Typography>
                        <Typography variant="h6" fontWeight="bold">
                          {activeSessions}
                        </Typography>
                      </Box>
                    </Tooltip>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Quick Actions */}
          <Typography variant="h5" sx={{ mb: 2, mt: 4 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                      <BoltIcon />
                    </Avatar>
                    <Typography variant="h6">Start Charging</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Initiate a new charging session automatically
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to="/charging" color="primary">
                    Charge Now
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                      <EvStationIcon />
                    </Avatar>
                    <Typography variant="h6">Find Stations</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Discover nearby charging stations
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to="/map" color="secondary">
                    View Map
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: '#ff9800', mr: 2 }}>
                      <WalletIcon />
                    </Avatar>
                    <Typography variant="h6">CDP Wallet</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Manage your crypto payments wallet
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to="/payments" color="warning">
                    View Wallet
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar sx={{ bgcolor: '#9c27b0', mr: 2 }}>
                      <HistoryIcon />
                    </Avatar>
                    <Typography variant="h6">Payment History</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    View your recent charging payments
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to="/payments" color="secondary">
                    View History
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>

          {/* Available Charging Stations */}
          <Typography variant="h5" sx={{ mb: 2, mt: 4 }}>
            Available Charging Stations
          </Typography>
          <Grid container spacing={3}>
            {stations.map((station) => (
              <Grid item xs={12} sm={6} md={4} key={station.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={1}>
                      <EvStationIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">{station.name}</Typography>
                    </Box>
                    <Typography variant="body2" gutterBottom>{station.location}</Typography>
                    
                    <Stack direction="row" spacing={1} mb={2}>
                      <Chip 
                        label={station.available ? 'Available' : 'In Use'} 
                        color={station.available ? 'success' : 'default'}
                        size="small"
                      />
                      <Chip 
                        label={`${station.power_kw} kW`}
                        color="info"
                        size="small"
                      />
                    </Stack>
                      <Box display="flex" justifyContent="space-between">
                      <Typography variant="body2">
                        <strong>Fiat:</strong> ₹{station.rate_kwh}/kWh
                      </Typography>
                      <Typography variant="body2">
                        <strong>USDC:</strong> ${station.rate_crypto}/kWh
                      </Typography>
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      component={Link} 
                      to={`/charging?station=${station.id}`}
                      disabled={!station.available}
                    >
                      Start Charging
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Recent Payments */}
          <Typography variant="h5" sx={{ mb: 2, mt: 4 }}>
            Recent Payments
          </Typography>
          {getRecentPayments().length > 0 ? (
            <Grid container spacing={3}>
              {getRecentPayments().map((payment, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" mb={1}>
                        <WalletIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="subtitle1">${payment.amount} {payment.currency}</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(payment.timestamp * 1000).toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                        Tx: {payment.tx_hash.substr(0, 8)}...{payment.tx_hash.substr(-6)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Paper sx={{ p: 3, borderRadius: 2, bgcolor: 'background.paper' }}>
              <Typography variant="body1" align="center" color="text.secondary">
                No payment history yet. Start charging to see payments here.
              </Typography>
            </Paper>
          )}
        </>
      )}
    </Box>
  );
};

export default Dashboard;
