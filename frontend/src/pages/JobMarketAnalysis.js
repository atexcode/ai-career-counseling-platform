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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  LocationOn,
  Work,
  AttachMoney
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const JobMarketAnalysis = () => {
  const { user, token } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    industry: '',
    location: '',
    experience_level: ''
  });
  const requestInProgress = useRef(false);

  const industries = [
    'Technology', 'Healthcare', 'Finance', 'Education', 'Marketing',
    'Engineering', 'Design', 'Sales', 'Human Resources', 'Consulting'
  ];

  const locations = [
    'Remote',
    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria',
    'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
    'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia',
    'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
    'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt',
    'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon',
    'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
    'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
    'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kosovo', 'Kuwait', 'Kyrgyzstan',
    'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar',
    'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
    'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal',
    'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan',
    'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
    'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia',
    'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
    'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
    'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
    'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
    'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
  ];

  const experienceLevels = [
    'Entry Level', 'Mid Level', 'Senior Level', 'Executive Level'
  ];

  const getJobMarketAnalysis = useCallback(async () => {
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
      const response = await api.get('/api/job-market/analysis', {
        params: {
          user_id: user._id,
          ...filters
        }
      });

      console.log('Job Market Analysis Response:', response.data);

      if (response.data && response.data.success && response.data.analysis) {
        setAnalysis(response.data.analysis);
      } else {
        console.error('Invalid response format:', response.data);
        setError('Failed to get job market analysis. Invalid response format.');
      }
    } catch (err) {
      console.error('Error fetching job market analysis:', err);
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching job market analysis. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
      requestInProgress.current = false;
    }
  }, [user, filters]);

  useEffect(() => {
    if (user) {
      getJobMarketAnalysis();
    }
  }, [user, getJobMarketAnalysis]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const applyFilters = () => {
    getJobMarketAnalysis();
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'High':
      case 'Increasing':
        return <TrendingUp color="success" />;
      case 'Low':
      case 'Decreasing':
        return <TrendingDown color="error" />;
      default:
        return <TrendingFlat color="warning" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'High':
      case 'Increasing':
        return 'success';
      case 'Low':
      case 'Decreasing':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Job Market Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Analyze current job market trends, salary data, and opportunities in your field.
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
              Filter Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
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

              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Location</InputLabel>
                  <Select
                    value={filters.location}
                    label="Location"
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                  >
                    <MenuItem value="">All Locations</MenuItem>
                    {locations.map(location => (
                      <MenuItem key={location} value={location}>{location}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
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

        {/* Analysis Results */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : analysis ? (
          <Grid container spacing={3}>
            {/* Market Overview */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Market Overview
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {analysis.overall_trends?.trend || 'Up'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Market Trend
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          ${analysis.average_salary?.toLocaleString() || '75,000'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Average Salary
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {analysis.industry_analysis?.length || 3}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Industries Analyzed
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Top Industries */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top Industries by Demand
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    {analysis.industry_analysis?.map((industry, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2">{industry.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {industry.growth}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          {getTrendIcon(industry.trend)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {industry.trend}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          Key Roles: {industry.key_roles?.join(', ')}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Top Locations */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Top Locations
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    {analysis.top_locations?.map((location, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <LocationOn color="primary" sx={{ mr: 1 }} />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="body2">{location.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {location.job_openings?.toLocaleString()} jobs • Avg: ${location.average_salary?.toLocaleString()}
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Market Insights */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Market Insights
                  </Typography>
                  <Typography variant="body1" paragraph>
                    {analysis.overall_trends?.description || 'The job market is experiencing growth with increasing demand for skilled professionals.'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={getJobMarketAnalysis}
                  disabled={loading}
                >
                  Refresh Analysis
                </Button>
                <Button
                  variant="outlined"
                  href="/career-recommendations"
                >
                  View Career Recommendations
                </Button>
              </Box>
            </Grid>
          </Grid>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" color="text.secondary">
                No job market analysis available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please update your profile and try again.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
};

export default JobMarketAnalysis;