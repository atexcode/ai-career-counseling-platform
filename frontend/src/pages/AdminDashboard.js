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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider
} from '@mui/material';
import {
  Delete,
  Edit,
  Add,
  Person,
  Work,
  TrendingUp,
  School,
  Assessment,
  Refresh
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const AdminDashboard = () => {
  const { user, token } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [careers, setCareers] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [editingItem, setEditingItem] = useState(null);

  // Form states
  const [userForm, setUserForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [careerForm, setCareerForm] = useState({
    title: '',
    description: '',
    industry: '',
    experience_level: '',
    salary_range: '',
    work_type: '',
    required_skills: []
  });
  const [skillForm, setSkillForm] = useState({
    name: '',
    category: '',
    description: '',
    difficulty_level: '',
    demand_level: ''
  });

  const getAdminStats = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.get('/api/admin/stats');

      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (err) {
      setError('Error fetching admin statistics');
    } finally {
      setLoading(false);
    }
  };

  const getUsers = async () => {
    try {
      const response = await api.get('/api/admin/users');

      if (response.data.success) {
        setUsers(response.data.users);
      }
    } catch (err) {
      setError('Error fetching users');
    }
  };

  const getCareers = async () => {
    try {
      const response = await api.get('/api/career/recommendations');

      if (response.data.success) {
        setCareers(response.data.careers || []);
      }
    } catch (err) {
      setError('Error fetching careers');
    }
  };

  const getSkills = async () => {
    try {
      const response = await api.get('/api/skills/analysis');

      if (response.data.success) {
        setSkills(response.data.skills || []);
      }
    } catch (err) {
      setError('Error fetching skills');
    }
  };

  useEffect(() => {
    if (user && user.role === 'admin') {
      getAdminStats();
      getUsers();
      getCareers();
      getSkills();
    }
  }, [user]);

  const handleOpenDialog = (type, item = null) => {
    setDialogType(type);
    setEditingItem(item);
    setOpenDialog(true);
    
    if (type === 'user' && item) {
      setUserForm({
        name: item.name,
        email: item.email,
        password: '',
        role: item.role
      });
    } else if (type === 'career' && item) {
      setCareerForm({
        title: item.title,
        description: item.description,
        industry: item.industry,
        experience_level: item.experience_level,
        salary_range: item.salary_range,
        work_type: item.work_type,
        required_skills: item.required_skills || []
      });
    } else if (type === 'skill' && item) {
      setSkillForm({
        name: item.name,
        category: item.category,
        description: item.description,
        difficulty_level: item.difficulty_level,
        demand_level: item.demand_level
      });
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setUserForm({ name: '', email: '', password: '', role: 'student' });
    setCareerForm({ title: '', description: '', industry: '', experience_level: '', salary_range: '', work_type: '', required_skills: [] });
    setSkillForm({ name: '', category: '', description: '', difficulty_level: '', demand_level: '' });
  };

  const handleSave = async () => {
    try {
      if (dialogType === 'user') {
        const endpoint = editingItem ? `/api/admin/users/${editingItem.id}` : '/api/admin/users';
        const method = editingItem ? 'put' : 'post';
        
        await api[method](endpoint, userForm);
        getUsers();
      } else if (dialogType === 'career') {
        const endpoint = editingItem ? `/api/career/recommendations/${editingItem._id}` : '/api/career/recommendations';
        const method = editingItem ? 'put' : 'post';
        
        await api[method](endpoint, careerForm);
        getCareers();
      } else if (dialogType === 'skill') {
        const endpoint = editingItem ? `/api/skills/analysis/${editingItem._id}` : '/api/skills/analysis';
        const method = editingItem ? 'put' : 'post';
        
        await api[method](endpoint, skillForm);
        getSkills();
      }
      
      handleCloseDialog();
    } catch (err) {
      setError('Failed to save item');
    }
  };

  const handleDelete = async (type, id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;

    try {
      if (type === 'user') {
        await api.delete(`/api/admin/users/${id}`);
        getUsers();
      } else if (type === 'career') {
        await api.delete(`/api/career/recommendations/${id}`);
        getCareers();
      } else if (type === 'skill') {
        await api.delete(`/api/skills/analysis/${id}`);
        getSkills();
      }
    } catch (err) {
      setError('Failed to delete item');
    }
  };

  if (user?.role !== 'admin') {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Alert severity="error">
            Access denied. Admin privileges required.
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage users, careers, skills, and system statistics.
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
            {/* Statistics Cards */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Person color="primary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats?.total_users || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Users
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Work color="secondary" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats?.total_careers || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Career Paths
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <School color="success" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats?.total_skills || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Skills Database
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp color="warning" sx={{ mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{stats?.active_sessions || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Sessions
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Users Management */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Users Management</Typography>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => handleOpenDialog('user')}
                    >
                      Add User
                    </Button>
                  </Box>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Email</TableCell>
                          <TableCell>Role</TableCell>
                          <TableCell>Created</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {users.map((user) => (
                          <TableRow key={user._id}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Avatar sx={{ mr: 2 }}>
                                  {user.name.charAt(0)}
                                </Avatar>
                                {user.name}
                              </Box>
                            </TableCell>
                            <TableCell>{user.email}</TableCell>
                            <TableCell>
                              <Chip
                                label={user.role}
                                color={user.role === 'admin' ? 'error' : 'primary'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {new Date(user.created_at).toLocaleDateString()}
                            </TableCell>
                            <TableCell>
                              <IconButton
                                size="small"
                                onClick={() => handleOpenDialog('user', user)}
                              >
                                <Edit />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDelete('user', user._id)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Careers Management */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Careers Management</Typography>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => handleOpenDialog('career')}
                    >
                      Add Career
                    </Button>
                  </Box>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Title</TableCell>
                          <TableCell>Industry</TableCell>
                          <TableCell>Experience Level</TableCell>
                          <TableCell>Salary Range</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {careers.map((career) => (
                          <TableRow key={career._id}>
                            <TableCell>{career.title}</TableCell>
                            <TableCell>{career.industry}</TableCell>
                            <TableCell>{career.experience_level}</TableCell>
                            <TableCell>{career.salary_range}</TableCell>
                            <TableCell>
                              <IconButton
                                size="small"
                                onClick={() => handleOpenDialog('career', career)}
                              >
                                <Edit />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDelete('career', career._id)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Skills Management */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">Skills Management</Typography>
                    <Button
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => handleOpenDialog('skill')}
                    >
                      Add Skill
                    </Button>
                  </Box>
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Difficulty</TableCell>
                          <TableCell>Demand</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {skills.map((skill) => (
                          <TableRow key={skill._id}>
                            <TableCell>{skill.name}</TableCell>
                            <TableCell>{skill.category}</TableCell>
                            <TableCell>{skill.difficulty_level}</TableCell>
                            <TableCell>{skill.demand_level}</TableCell>
                            <TableCell>
                              <IconButton
                                size="small"
                                onClick={() => handleOpenDialog('skill', skill)}
                              >
                                <Edit />
                              </IconButton>
                              <IconButton
                                size="small"
                                onClick={() => handleDelete('skill', skill._id)}
                                color="error"
                              >
                                <Delete />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Refresh Button */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => {
                    getAdminStats();
                    getUsers();
                    getCareers();
                    getSkills();
                  }}
                >
                  Refresh All Data
                </Button>
              </Box>
            </Grid>
          </Grid>
        )}

        {/* Dialog for Add/Edit */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingItem ? `Edit ${dialogType}` : `Add ${dialogType}`}
          </DialogTitle>
          <DialogContent>
            {dialogType === 'user' && (
              <Box sx={{ pt: 1 }}>
                <TextField
                  fullWidth
                  label="Name"
                  value={userForm.name}
                  onChange={(e) => setUserForm(prev => ({ ...prev, name: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Email"
                  value={userForm.email}
                  onChange={(e) => setUserForm(prev => ({ ...prev, email: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  value={userForm.password}
                  onChange={(e) => setUserForm(prev => ({ ...prev, password: e.target.value }))}
                  margin="normal"
                />
                <FormControl fullWidth margin="normal">
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={userForm.role}
                    label="Role"
                    onChange={(e) => setUserForm(prev => ({ ...prev, role: e.target.value }))}
                  >
                    <MenuItem value="student">Student</MenuItem>
                    <MenuItem value="professional">Professional</MenuItem>
                    <MenuItem value="career_changer">Career Changer</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}

            {dialogType === 'career' && (
              <Box sx={{ pt: 1 }}>
                <TextField
                  fullWidth
                  label="Title"
                  value={careerForm.title}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, title: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={careerForm.description}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, description: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Industry"
                  value={careerForm.industry}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, industry: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Experience Level"
                  value={careerForm.experience_level}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, experience_level: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Salary Range"
                  value={careerForm.salary_range}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, salary_range: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Work Type"
                  value={careerForm.work_type}
                  onChange={(e) => setCareerForm(prev => ({ ...prev, work_type: e.target.value }))}
                  margin="normal"
                />
              </Box>
            )}

            {dialogType === 'skill' && (
              <Box sx={{ pt: 1 }}>
                <TextField
                  fullWidth
                  label="Name"
                  value={skillForm.name}
                  onChange={(e) => setSkillForm(prev => ({ ...prev, name: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Category"
                  value={skillForm.category}
                  onChange={(e) => setSkillForm(prev => ({ ...prev, category: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={skillForm.description}
                  onChange={(e) => setSkillForm(prev => ({ ...prev, description: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Difficulty Level"
                  value={skillForm.difficulty_level}
                  onChange={(e) => setSkillForm(prev => ({ ...prev, difficulty_level: e.target.value }))}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Demand Level"
                  value={skillForm.demand_level}
                  onChange={(e) => setSkillForm(prev => ({ ...prev, demand_level: e.target.value }))}
                  margin="normal"
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button onClick={handleSave} variant="contained">
              {editingItem ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default AdminDashboard;