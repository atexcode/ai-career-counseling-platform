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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Rating
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const CareerRecommendations = () => {
  const { user, token } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    experience_level: '',
    industry: '',
    salary_range: '',
    work_type: ''
  });
  const requestInProgress = useRef(false);

  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Education', 'Marketing',
    'Engineering', 'Design', 'Sales', 'Human Resources', 'Consulting'
  ];

  const experienceLevels = [
    'Entry Level', 'Mid Level', 'Senior Level', 'Executive Level'
  ];

  const salaryRanges = [
    'Under $30k', '$30k-$50k', '$50k-$75k', '$75k-$100k', 
    '$100k-$150k', '$150k+'
  ];

  const workTypes = [
    'Full-time', 'Part-time', 'Contract', 'Freelance', 'Remote', 'Hybrid'
  ];

  const getRecommendations = useCallback(async () => {
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
      const response = await api.get('/api/career/recommendations', {
        params: {
          user_id: user._id,
          ...filters
        }
      });

      console.log('Career Recommendations Response:', response.data);

      if (response.data && response.data.success && response.data.recommendations) {
        setRecommendations(response.data.recommendations);
      } else {
        console.error('Invalid response format:', response.data);
        setError('Failed to get recommendations. Invalid response format.');
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching recommendations. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
      requestInProgress.current = false;
    }
  }, [user, filters]);

  useEffect(() => {
    if (user) {
      getRecommendations();
    }
  }, [user, getRecommendations]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const applyFilters = () => {
    getRecommendations();
  };

  const saveRecommendation = async (careerId) => {
    try {
      await api.post('/api/career/save', {
        career_id: careerId,
        user_id: user._id
      });
    } catch (err) {
      console.error('Failed to save recommendation:', err);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Career Recommendations
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Get personalized career recommendations based on your profile and preferences.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Filter Recommendations
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Experience Level</InputLabel>
                  <Select
                    value={filters.experience_level}
                    label="Experience Level"
                    onChange={(e) => handleFilterChange('experience_level', e.target.value)}
                  >
                    <MenuItem value="">All Levels</MenuItem>
                    {experienceLevels.map(level => (
                      <MenuItem key={level} value={level}>{level}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Industry</InputLabel>
                  <Select
                    value={filters.industry}
                    label="Industry"
                    onChange={(e) => handleFilterChange('industry', e.target.value)}
                  >
                    <MenuItem value="">All Industries</MenuItem>
                    {industries.map(industry => (
                      <MenuItem key={industry} value={industry}>{industry}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Salary Range</InputLabel>
                  <Select
                    value={filters.salary_range}
                    label="Salary Range"
                    onChange={(e) => handleFilterChange('salary_range', e.target.value)}
                  >
                    <MenuItem value="">All Ranges</MenuItem>
                    {salaryRanges.map(range => (
                      <MenuItem key={range} value={range}>{range}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Work Type</InputLabel>
                  <Select
                    value={filters.work_type}
                    label="Work Type"
                    onChange={(e) => handleFilterChange('work_type', e.target.value)}
                  >
                    <MenuItem value="">All Types</MenuItem>
                    {workTypes.map(type => (
                      <MenuItem key={type} value={type}>{type}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Button
                  variant="contained"
                  onClick={applyFilters}
                  disabled={loading}
                  sx={{ mt: 2 }}
                >
                  Apply Filters
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Recommendations */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {recommendations.map((career, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {career.title}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {career.description}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Match Score
                      </Typography>
                      <Rating
                        value={career.match_score / 20}
                        readOnly
                        precision={0.1}
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary">
                        {career.match_score}% match
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Required Skills
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {career.required_skills?.slice(0, 5).map((skill, skillIndex) => (
                          <Chip
                            key={skillIndex}
                            label={skill}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                        ))}
                        {career.required_skills?.length > 5 && (
                          <Chip
                            label={`+${career.required_skills.length - 5} more`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Details
                      </Typography>
                      <Typography variant="body2">
                        <strong>Industry:</strong> {career.industry}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Experience Level:</strong> {career.experience_level}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Salary Range:</strong> {career.salary_range}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Work Type:</strong> {career.work_type}
                      </Typography>
                    </Box>
                  </CardContent>

                  <Box sx={{ p: 2, pt: 0 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => saveRecommendation(career.id)}
                    >
                      Save Recommendation
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}

            {recommendations.length === 0 && !loading && (
              <Grid item xs={12}>
                <Card>
                  <CardContent sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                      No recommendations found
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Try adjusting your filters or update your profile for better recommendations.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default CareerRecommendations;