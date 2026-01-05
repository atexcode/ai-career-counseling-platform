import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Container
} from '@mui/material';
import {
  School,
  Psychology,
  Work,
  Chat,
  Assessment,
  TrendingUp
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Career Recommendations',
      description: 'Get personalized career recommendations based on your skills and interests',
      icon: <School sx={{ fontSize: 40 }} />,
      color: '#1976d2'
    },
    {
      title: 'Skills Analysis',
      description: 'Analyze your current skills and identify areas for improvement',
      icon: <Assessment sx={{ fontSize: 40 }} />,
      color: '#dc004e'
    },
    {
      title: 'Job Market Analysis',
      description: 'Explore current job market trends and opportunities',
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      color: '#2e7d32'
    },
    {
      title: 'AI Chatbot',
      description: 'Chat with our AI counselor for personalized career guidance',
      icon: <Chat sx={{ fontSize: 40 }} />,
      color: '#ed6c02'
    },
    {
      title: 'Career Planning',
      description: 'Create and track your career development plan',
      icon: <Psychology sx={{ fontSize: 40 }} />,
      color: '#9c27b0'
    },
    {
      title: 'Job Search',
      description: 'Find relevant job opportunities matching your profile',
      icon: <Work sx={{ fontSize: 40 }} />,
      color: '#d32f2f'
    }
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Welcome to AI Career Counseling Platform
        </Typography>
        <Typography variant="h6" component="h2" gutterBottom align="center" color="text.secondary">
          Your personalized career development journey starts here
        </Typography>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 3
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                  <Box sx={{ color: feature.color, mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {feature.description}
                  </Typography>
                  <Button 
                    variant="contained" 
                    sx={{ 
                      backgroundColor: feature.color,
                      '&:hover': {
                        backgroundColor: feature.color,
                        opacity: 0.9
                      }
                    }}
                    fullWidth
                  >
                    Explore
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => navigate('/login')}
          >
            Back to Login
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard;



