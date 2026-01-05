import React, { useState, useEffect, useCallback } from 'react';
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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  CheckCircle,
  RadioButtonUnchecked,
  School,
  Work,
  TrendingUp,
  Schedule,
  Add,
  Save
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const CareerPlanning = () => {
  const { user, token } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [newGoal, setNewGoal] = useState('');
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    deadline: '',
    priority: 'medium'
  });

  const steps = [
    'Define Career Goals',
    'Assess Current Skills',
    'Identify Skill Gaps',
    'Create Learning Plan',
    'Set Milestones',
    'Track Progress'
  ];

  const getCareerPlan = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.get('/api/career/plan', {
        params: {
          user_id: user._id
        }
      });

      if (response.data.success) {
        setPlan(response.data.plan);
      } else {
        setError('Failed to get career plan');
      }
    } catch (err) {
      setError('Error fetching career plan. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      getCareerPlan();
    }
  }, [user, getCareerPlan]);

  const addGoal = async () => {
    if (!newGoal.trim()) return;

    try {
      const response = await api.post('/api/career/goals', {
        goal: newGoal.trim(),
        user_id: user._id
      });

      if (response.data.success) {
        setNewGoal('');
        getCareerPlan(); // Refresh the plan
      }
    } catch (err) {
      setError('Failed to add goal');
    }
  };

  const toggleGoalComplete = async (goalId) => {
    try {
      await api.put(`/api/career/goals/${goalId}`, {
        user_id: user._id
      });
      getCareerPlan(); // Refresh the plan
    } catch (err) {
      setError('Failed to update goal');
    }
  };

  const addMilestone = async () => {
    if (!newMilestone.title.trim()) return;

    try {
      const response = await api.post('/api/career/milestones', {
        ...newMilestone,
        user_id: user._id
      });

      if (response.data.success) {
        setNewMilestone({
          title: '',
          description: '',
          deadline: '',
          priority: 'medium'
        });
        getCareerPlan(); // Refresh the plan
      }
    } catch (err) {
      setError('Failed to add milestone');
    }
  };

  const toggleMilestoneComplete = async (milestoneId) => {
    try {
      await api.put(`/api/career/milestones/${milestoneId}`, {
        user_id: user._id
      });
      getCareerPlan(); // Refresh the plan
    } catch (err) {
      setError('Failed to update milestone');
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'high': 'error',
      'medium': 'warning',
      'low': 'success'
    };
    return colors[priority] || 'default';
  };

  const calculateProgress = () => {
    if (!plan?.milestones) return 0;
    const completed = plan.milestones.filter(m => m.completed).length;
    return (completed / plan.milestones.length) * 100;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Career Planning
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Create and track your personalized career development plan with goals, milestones, and progress tracking.
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
        ) : (
          <Grid container spacing={3}>
            {/* Progress Overview */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Overall Progress
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Career Plan Progress</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {Math.round(calculateProgress())}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={calculateProgress()}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="primary">
                          {plan?.goals?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Goals
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="success.main">
                          {plan?.goals?.filter(g => g.completed).length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Completed Goals
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="warning.main">
                          {plan?.milestones?.length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Milestones
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h4" color="info.main">
                          {plan?.milestones?.filter(m => m.completed).length || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Completed Milestones
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Career Goals */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Career Goals
                  </Typography>
                  
                  {/* Add New Goal */}
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Add a new career goal..."
                      value={newGoal}
                      onChange={(e) => setNewGoal(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addGoal()}
                    />
                    <Button
                      variant="contained"
                      onClick={addGoal}
                      disabled={!newGoal.trim()}
                      size="small"
                    >
                      <Add />
                    </Button>
                  </Box>

                  {/* Goals List */}
                  <List>
                    {plan?.goals?.map((goal, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          <Checkbox
                            checked={goal.completed}
                            onChange={() => toggleGoalComplete(goal.id)}
                            icon={<RadioButtonUnchecked />}
                            checkedIcon={<CheckCircle />}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={goal.text}
                          secondary={goal.created_at ? new Date(goal.created_at).toLocaleDateString() : ''}
                          sx={{
                            textDecoration: goal.completed ? 'line-through' : 'none',
                            opacity: goal.completed ? 0.6 : 1
                          }}
                        />
                      </ListItem>
                    ))}
                    {(!plan?.goals || plan.goals.length === 0) && (
                      <ListItem>
                        <ListItemText
                          primary="No goals set yet"
                          secondary="Add your first career goal to get started"
                        />
                      </ListItem>
                    )}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Milestones */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Milestones
                  </Typography>

                  {/* Add New Milestone */}
                  <Box sx={{ mb: 2 }}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Milestone Title"
                      value={newMilestone.title}
                      onChange={(e) => setNewMilestone(prev => ({ ...prev, title: e.target.value }))}
                      sx={{ mb: 1 }}
                    />
                    <TextField
                      fullWidth
                      size="small"
                      label="Description"
                      multiline
                      rows={2}
                      value={newMilestone.description}
                      onChange={(e) => setNewMilestone(prev => ({ ...prev, description: e.target.value }))}
                      sx={{ mb: 1 }}
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <TextField
                        size="small"
                        type="date"
                        label="Deadline"
                        value={newMilestone.deadline}
                        onChange={(e) => setNewMilestone(prev => ({ ...prev, deadline: e.target.value }))}
                        InputLabelProps={{ shrink: true }}
                        sx={{ flexGrow: 1 }}
                      />
                      <FormControl size="small" sx={{ minWidth: 100 }}>
                        <InputLabel>Priority</InputLabel>
                        <Select
                          value={newMilestone.priority}
                          label="Priority"
                          onChange={(e) => setNewMilestone(prev => ({ ...prev, priority: e.target.value }))}
                        >
                          <MenuItem value="low">Low</MenuItem>
                          <MenuItem value="medium">Medium</MenuItem>
                          <MenuItem value="high">High</MenuItem>
                        </Select>
                      </FormControl>
                      <Button
                        variant="contained"
                        onClick={addMilestone}
                        disabled={!newMilestone.title.trim()}
                        size="small"
                      >
                        <Add />
                      </Button>
                    </Box>
                  </Box>

                  {/* Milestones List */}
                  <List>
                    {plan?.milestones?.map((milestone, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          <Checkbox
                            checked={milestone.completed}
                            onChange={() => toggleMilestoneComplete(milestone.id)}
                            icon={<RadioButtonUnchecked />}
                            checkedIcon={<CheckCircle />}
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {milestone.title}
                              <Chip
                                label={milestone.priority}
                                size="small"
                                color={getPriorityColor(milestone.priority)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {milestone.description}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Deadline: {milestone.deadline ? new Date(milestone.deadline).toLocaleDateString() : 'No deadline'}
                              </Typography>
                            </Box>
                          }
                          sx={{
                            textDecoration: milestone.completed ? 'line-through' : 'none',
                            opacity: milestone.completed ? 0.6 : 1
                          }}
                        />
                      </ListItem>
                    ))}
                    {(!plan?.milestones || plan.milestones.length === 0) && (
                      <ListItem>
                        <ListItemText
                          primary="No milestones set yet"
                          secondary="Add milestones to track your progress"
                        />
                      </ListItem>
                    )}
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Learning Plan */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Learning Plan
                  </Typography>
                  <Grid container spacing={2}>
                    {plan?.learning_plan?.map((item, index) => (
                      <Grid item xs={12} md={4} key={index}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              {item.type === 'course' && <School color="primary" sx={{ mr: 1 }} />}
                              {item.type === 'certification' && <Work color="secondary" sx={{ mr: 1 }} />}
                              {item.type === 'practice' && <TrendingUp color="success" sx={{ mr: 1 }} />}
                              <Typography variant="subtitle1">
                                {item.title}
                              </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary" paragraph>
                              {item.description}
                            </Typography>
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                Duration: {item.duration}
                              </Typography>
                            </Box>
                            <Box sx={{ mb: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                Difficulty: {item.difficulty}
                              </Typography>
                            </Box>
                            <Button
                              variant="outlined"
                              size="small"
                              href={item.resource_url}
                              target="_blank"
                              fullWidth
                            >
                              Start Learning
                            </Button>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                    {(!plan?.learning_plan || plan.learning_plan.length === 0) && (
                      <Grid item xs={12}>
                        <Box sx={{ textAlign: 'center', py: 4 }}>
                          <Typography variant="h6" color="text.secondary">
                            No learning plan available
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Complete your skills analysis to get personalized learning recommendations
                          </Typography>
                          <Button
                            variant="contained"
                            href="/skills-analysis"
                            sx={{ mt: 2 }}
                          >
                            Analyze Skills
                          </Button>
                        </Box>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Action Buttons */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={getCareerPlan}
                  disabled={loading}
                >
                  Refresh Plan
                </Button>
                <Button
                  variant="outlined"
                  href="/skills-analysis"
                >
                  Update Skills Analysis
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
        )}
      </Box>
    </Container>
  );
};

export default CareerPlanning;