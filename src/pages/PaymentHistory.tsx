import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Button,
  Grid,
  Divider,
  Link,
} from '@mui/material';
import {
  AccountBalanceWallet as WalletIcon,
  LocalAtm as AtmIcon,
  History as HistoryIcon,
  Launch as LaunchIcon,
} from '@mui/icons-material';
import axios from 'axios';

// Types
interface PaymentRecord {
  amount: number;
  currency: string;
  timestamp: number;
  tx_hash: string;
  session_id: string;
}

const PaymentHistory: React.FC = () => {
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  
  // Mock wallet data
  const walletData = {
    address: '0x7a16fF8270133F063aAb6C9977183D9e72835428',
    balance: 75.45,
    network: 'Base-Sepolia',
  };
  
  useEffect(() => {
    const fetchPayments = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/payments');
        setPayments(response.data.payments || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching payment history:', err);
        setError('Failed to load payment history. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPayments();
  }, []);
  
  // Calculate total spent
  const getTotalSpent = (): number => {
    return payments.reduce((total, payment) => total + payment.amount, 0);
  };
  
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  return (
    <Box sx={{ mt: 8 }}>
      <Typography variant="h4" component="h1" fontWeight="500" gutterBottom>
        Payment History
      </Typography>
      
      <Grid container spacing={4}>
        {/* Wallet Summary */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Box display="flex" alignItems="center" mb={2}>
              <WalletIcon color="primary" sx={{ mr: 1, fontSize: 28 }} />
              <Typography variant="h5">CDP Wallet</Typography>
            </Box>
            
            <Divider sx={{ mb: 3 }} />
            
            <Box mb={4}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Wallet Address:
              </Typography>
              <Box display="flex" alignItems="center">
                <Typography
                  variant="body2"
                  sx={{ fontFamily: 'monospace', flexGrow: 1 }}
                >
                  {walletData.address}
                </Typography>
                <Link 
                  href={`https://sepolia.basescan.org/address/${walletData.address}`}
                  target="_blank"
                  rel="noopener"
                >
                  <LaunchIcon fontSize="small" />
                </Link>
              </Box>
            </Box>
            
            <Box mb={4}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Network:
              </Typography>
              <Chip 
                label={walletData.network} 
                color="secondary" 
                size="small"
              />
            </Box>
            
            <Box mb={2}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                USDC Balance:
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="primary">
                ${walletData.balance.toFixed(2)}
              </Typography>
            </Box>
            
            {/* Add Funds Button */}
            <Button 
              variant="outlined"
              fullWidth
              startIcon={<AtmIcon />}
              sx={{ mt: 2 }}
            >
              Add Funds
            </Button>
          </Paper>
        </Grid>
        
        {/* Payment History */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Box display="flex" alignItems="center" mb={3}>
              <HistoryIcon color="primary" sx={{ mr: 1, fontSize: 28 }} />
              <Typography variant="h5">Transaction History</Typography>
            </Box>
            
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
              <Box>
                {/* Summary Card */}
                <Card sx={{ mb: 4, bgcolor: 'primary.dark' }}>
                  <CardContent>
                    <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} justifyContent="space-between">
                      <Box mb={{ xs: 2, sm: 0 }}>                        <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                          Total Spent
                        </Typography>
                        <Typography variant="h4" color="white" fontWeight="bold">
                          ${getTotalSpent().toFixed(2)} USDC
                        </Typography>
                      </Box>
                      
                      <Box>                        <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
                          Total Transactions
                        </Typography>
                        <Typography variant="h4" color="white" fontWeight="bold">
                          {payments.length}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
                
                {/* Transactions Table */}
                {payments.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Amount</TableCell>
                          <TableCell>Transaction</TableCell>
                          <TableCell>Session ID</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {payments
                          .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                          .map((payment, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                {new Date(payment.timestamp * 1000).toLocaleString()}
                              </TableCell>
                              <TableCell>
                                <Box display="flex" alignItems="center">
                                  <Typography fontWeight="bold" color="error">
                                    -${payment.amount}
                                  </Typography>
                                  <Chip 
                                    label={payment.currency} 
                                    size="small" 
                                    color="default" 
                                    sx={{ ml: 1 }}
                                  />
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Link 
                                  href={`https://sepolia.basescan.org/tx/${payment.tx_hash}`}
                                  target="_blank"
                                  rel="noopener"
                                  sx={{ 
                                    display: 'flex',
                                    alignItems: 'center',
                                    fontFamily: 'monospace'
                                  }}
                                >
                                  {`${payment.tx_hash.substring(0, 8)}...${payment.tx_hash.substring(payment.tx_hash.length - 6)}`}
                                  <LaunchIcon fontSize="small" sx={{ ml: 0.5 }} />
                                </Link>
                              </TableCell>
                              <TableCell>
                                {payment.session_id}
                              </TableCell>
                            </TableRow>
                          ))}
                      </TableBody>
                    </Table>
                    
                    <TablePagination
                      rowsPerPageOptions={[5, 10, 25]}
                      component="div"
                      count={payments.length}
                      rowsPerPage={rowsPerPage}
                      page={page}
                      onPageChange={handleChangePage}
                      onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                  </TableContainer>
                ) : (
                  <Box textAlign="center" py={4}>
                    <Typography color="text.secondary">
                      No payment records found.
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PaymentHistory;
