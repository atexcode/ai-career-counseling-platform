import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  TrendingUp,
  School,
  Work
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const SkillsAnalysis = () => {
  const { user, token } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const requestInProgress = useRef(false);

  const getSkillsAnalysis = useCallback(async () => {
    if (requestInProgress.current) {
      return; // Prevent duplicate requests
    }

    if (!user || !user._id) {
      setError('User information not available. Please log in again.');
      setLoading(false);
      return;
    }

    requestInProgress.current = true;
    setLoading(true);
    setError('');

    try {
      const response = await api.get('/api/skills/analysis', {
        params: {
          user_id: user._id
        }
      });

      console.log('Skills Analysis Response:', response.data);

      if (response.data && response.data.success && response.data.analysis) {
        setAnalysis(response.data.analysis);
      } else {
        console.error('Invalid response format:', response.data);
        setError('Failed to get skills analysis. Invalid response format.');
      }
    } catch (err) {
      console.error('Error fetching skills analysis:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching skills analysis. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
      requestInProgress.current = false;
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      getSkillsAnalysis();
    }
  }, [user, getSkillsAnalysis]);

  const getSkillLevel = (level) => {
    const levels = {
      'beginner': { color: 'error', label: 'Beginner' },
      'intermediate': { color: 'warning', label: 'Intermediate' },
      'advanced': { color: 'success', label: 'Advanced' },
      'expert': { color: 'success', label: 'Expert' }
    };
    return levels[level] || { color: 'default', label: 'Unknown' };
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'high': 'error',
      'medium': 'warning',
      'low': 'success'
    };
    return colors[priority] || 'default';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Skills Gap Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Analyze your current skills and identify areas for improvement to achieve your career goals.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : analysis ? (
          <Grid container spacing={3}>
            {/* Skills Overview */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Skills Overview
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {analysis.user_skills?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Your Skills
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {analysis.required_skills_for_goals?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Required Skills
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {analysis.skills_gap?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Skills Gap
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="error.main">
                          {analysis.learning_recommendations?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Recommendations
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Current Skills */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Your Current Skills
                  </Typography>
                  <List>
                    {analysis.user_skills?.map((skill, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          <CheckCircle color="success" />
                        </ListItemIcon>
                        <ListItemText
                          primary={skill}
                          secondary="Current skill"
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Skills Gap */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Skills Gap Analysis
                  </Typography>
                  <List>
                    {analysis.skills_gap?.map((skill, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          <Cancel color="error" />
                        </ListItemIcon>
                        <ListItemText
                          primary={skill}
                          secondary="Missing skill for your career goals"
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Learning Recommendations */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Learning Recommendations
                  </Typography>
                  <Grid container spacing={2}>
                    {analysis.learning_recommendations?.map((rec, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              <School color="primary" sx={{ mr: 1 }} />
                              <Typography variant="subtitle1">
                                {rec.skill}
                              </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary" paragraph>
                              {rec.description}
                            </Typography>
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="caption" color="text.secondary">
                                Resources: {rec.resources?.join(', ')}
                              </Typography>
                            </Box>
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="caption" color="text.secondary">
                                Projects: {rec.projects?.join(', ')}
                              </Typography>
                            </Box>
                            <Button
                              variant="outlined"
                              size="small"
                              fullWidth
                            >
                              Start Learning
                            </Button>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={getSkillsAnalysis}
                  disabled={loading}
                >
                  Refresh Analysis
                </Button>
                <Button
                  variant="outlined"
                  href="/career-planning"
                >
                  Create Learning Plan
                </Button>
              </Box>
            </Grid>
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No skills analysis available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please update your profile with skills information to get a comprehensive analysis.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
};

export default SkillsAnalysis;