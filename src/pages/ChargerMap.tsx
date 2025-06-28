import React, { useEffect, useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Chip,
  TextField,
  Button,
  CircularProgress,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';
import { Search as SearchIcon, Map as MapIcon, Info } from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Types
interface ChargingStation {
  id: string;
  name: string;
  location: string;
  available: boolean;
  rate_kwh: number;
  rate_crypto: number;
  power_kw: number;
  lat: number;
  lng: number;
  price?: number;
}

// Bangalore center coordinates
const bangaloreCenter = {
  lat: 12.9716,
  lng: 77.5946,
};

const ChargerMap: React.FC = () => {
  const navigate = useNavigate();
  const [stations, setStations] = useState<ChargingStation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState<string>('');
  const [selectedStation, setSelectedStation] = useState<ChargingStation | null>(null);
  const [notificationOpen, setNotificationOpen] = useState(false);

  // Handlers
  const onMarkerClick = (station: ChargingStation) => {
    setSelectedStation(station);
  };

  const startCharging = (stationId: string) => {
    navigate(`/charging?station=${stationId}`);
  };
  
  const handleNotificationClose = () => {
    setNotificationOpen(false);
  };

  useEffect(() => {
    const fetchStations = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/discover');
        setStations(response.data.stations || []);
        setError(null);
        setNotificationOpen(true);
      } catch (err) {
        console.error('Error fetching charging stations:', err);
        setError('Failed to load charging stations. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStations();
  }, []);

  const filteredStations = useMemo(() => 
    stations.filter(station => 
      station.name.toLowerCase().includes(search.toLowerCase()) || 
      station.location.toLowerCase().includes(search.toLowerCase())
    ),
  [stations, search]);

  return (
    <Box sx={{ mt: 8 }}>
      <Snackbar 
        open={notificationOpen} 
        autoHideDuration={6000} 
        onClose={handleNotificationClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleNotificationClose} severity="info" sx={{ width: '100%' }}>
          <Box>
            <Typography variant="subtitle1" fontWeight="bold">Demo Mode</Typography>
            <Typography variant="body2">
              This is a simulated map of ChargeX stations in Bangalore. 
              Select a station to start a charging session.
            </Typography>
          </Box>
        </Alert>
      </Snackbar>
      
      <Typography variant="h4" component="h1" fontWeight="500" gutterBottom>
        Charging Stations Map
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <MapIcon sx={{ fontSize: 32, mr: 2, color: 'primary.main' }} />
          <Typography variant="h5">Find Available Chargers in Greater Bangalore</Typography>
        </Box>
        
        <Box display="flex" mb={4}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search by name or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ mr: 2 }}
          />
          <Button 
            variant="contained" 
            color="primary"
            startIcon={<SearchIcon />}
          >
            Search
          </Button>
        </Box>
        
        {/* Interactive Map View */}
        <Box
          sx={{
            height: 450,
            borderRadius: 1,
            mb: 4,
            position: 'relative',
            border: '1px solid #e0e0e0',
            backgroundImage: 'linear-gradient(45deg, #f5f5f5 25%, transparent 25%), linear-gradient(-45deg, #f5f5f5 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f5f5f5 75%), linear-gradient(-45deg, transparent 75%, #f5f5f5 75%)',
            backgroundSize: '20px 20px',
            backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
          }}
        >
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" height="100%">
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Box 
                display="flex" 
                justifyContent="center" 
                alignItems="center" 
                height="100%" 
                flexDirection="column"
              >
                <MapIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                <Typography color="primary.main" variant="h6" gutterBottom>
                  Interactive Map of Bangalore Charging Stations
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ maxWidth: 400 }}>
                  This demo shows {stations.length} ChargeX charging stations across Greater Bangalore.
                  Click on the markers below to select a station.
                </Typography>
              </Box>
              
              {/* Interactive station markers */}
              {stations.slice(0, 7).map((station, index) => (
                <Box
                  key={station.id}
                  sx={{
                    position: 'absolute',
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    bgcolor: station.available ? '#4caf50' : '#757575',
                    border: '3px solid white',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
                    top: `${15 + (index * 12) + Math.sin(index * 2.5) * 85}px`,
                    left: `${15 + (index * 30) + Math.cos(index * 2.5) * 150}px`,
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    zIndex: selectedStation?.id === station.id ? 100 : 10,
                    transform: selectedStation?.id === station.id ? 'scale(2)' : 'scale(1)',
                    '&:hover': {
                      transform: 'scale(1.8)',
                      zIndex: 99,
                    },
                  }}
                  onClick={() => onMarkerClick(station)}
                  title={station.name}
                />
              ))}
              
              {/* Info popup for selected station */}
              {selectedStation && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    bgcolor: 'white',
                    p: 2,
                    borderRadius: 2,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                    border: '2px solid #1976d2',
                    maxWidth: 280,
                    zIndex: 1000,
                  }}
                >
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                    {selectedStation.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {selectedStation.location}
                  </Typography>
                  <Box display="flex" alignItems="center" my={1}>
                    <Chip 
                      label={selectedStation.available ? 'Available' : 'In Use'} 
                      color={selectedStation.available ? 'success' : 'default'}
                      size="small"
                      sx={{ mr: 1 }}
                    />
                    <Chip 
                      label={`${selectedStation.power_kw} kW`}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Price:</strong> ₹{selectedStation.rate_kwh}/kWh ({selectedStation.rate_crypto} USDC/kWh)
                  </Typography>
                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      onClick={() => setSelectedStation(null)}
                    >
                      Close
                    </Button>
                    {selectedStation.available && (
                      <Button 
                        variant="contained" 
                        color="primary" 
                        size="small" 
                        onClick={() => startCharging(selectedStation.id)}
                      >
                        Start Charging
                      </Button>
                    )}
                  </Box>
                </Box>
              )}
            </>
          )}
          
          <Box 
            sx={{ 
              position: 'absolute', 
              bottom: 5, 
              left: 5, 
              bgcolor: 'rgba(255,255,255,0.9)', 
              p: 1, 
              borderRadius: 1,
              fontSize: '0.75rem',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <Info fontSize="inherit" sx={{ mr: 0.5 }} /> 
            Demo Map View - Click markers to select stations
          </Box>
        </Box>
        
        {/* Stations list */}
        <Typography variant="h6" gutterBottom>Nearby Stations</Typography>
        
        {loading ? (
          <Box display="flex" justifyContent="center" my={4}>
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
          <Grid container spacing={3}>
            {filteredStations.length > 0 ? (
              filteredStations.map((station) => (
                <Grid item xs={12} sm={6} md={4} key={station.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedStation?.id === station.id ? '2px solid #1976d2' : 'none',
                      '&:hover': {
                        boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
                      }
                    }}
                    onClick={() => onMarkerClick(station)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>{station.name}</Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {station.location}
                      </Typography>
                      
                      <Box display="flex" mt={1} mb={2}>
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
                        />
                      </Box>
                      
                      <Box display="flex" justifyContent="space-between" mb={2}>
                        <Typography variant="body2">
                          <strong>Fiat:</strong> ₹{station.rate_kwh}/kWh
                        </Typography>
                        <Typography variant="body2">
                          <strong>USDC:</strong> ${station.rate_crypto}/kWh
                        </Typography>
                      </Box>
                      
                      {station.available && (
                        <Button 
                          variant="contained" 
                          color="primary" 
                          size="small" 
                          fullWidth
                          onClick={(e) => {
                            e.stopPropagation();
                            startCharging(station.id);
                          }}
                        >
                          Start Charging
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Typography variant="body1" align="center" color="text.secondary">
                  No stations match your search criteria.
                </Typography>
              </Grid>
            )}
          </Grid>
        )}
      </Paper>
    </Box>
  );
};

export default ChargerMap;
