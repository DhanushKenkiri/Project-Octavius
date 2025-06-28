import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Box,
  Divider,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Map as MapIcon,
  EvStation as EvStationIcon,
  Payment as PaymentIcon,
  SmartToy as AgentIcon,
  BatteryChargingFull as BatteryIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

const Navigation: React.FC = () => {
  const location = useLocation();

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Charger Map', icon: <MapIcon />, path: '/map' },
    { text: 'Charging Session', icon: <EvStationIcon />, path: '/charging' },
    { text: 'Payment History', icon: <PaymentIcon />, path: '/payments' },
    { text: 'Agent Console', icon: <AgentIcon />, path: '/agent' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          px: [1],
          py: 2,
          backgroundColor: 'primary.dark',
        }}
      >
        <BatteryIcon sx={{ fontSize: 32, mr: 1 }} />
        <Typography variant="h6" noWrap component="div" fontWeight="bold">
          ChargeX Agent
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            component={Link}
            to={item.path}
            selected={location.pathname === item.path}
            sx={{
              '&.Mui-selected': {
                backgroundColor: 'primary.dark',
                '&:hover': {
                  backgroundColor: 'primary.main',
                },
              },
              '&:hover': {
                backgroundColor: 'action.hover',
              },
              my: 0.5,
              mx: 1,
              borderRadius: 1,
            }}
          >
            <ListItemIcon 
              sx={{ 
                color: location.pathname === item.path ? 'white' : 'inherit',
                minWidth: 40,
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Box sx={{ flexGrow: 1 }} />
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          Powered by Amazon Bedrock
        </Typography>
        <Typography variant="caption" color="text.secondary" align="center" display="block">
          & Coinbase CDP Wallets
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Navigation;
