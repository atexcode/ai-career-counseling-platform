import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Chip,
  Alert,
  Divider,
  Avatar
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { humanizeFieldName, shouldDisplayField, getInputType } from '../utils/fieldUtils';

const Profile = () => {
  const { user: authUser } = useAuth();
  const [profile, setProfile] = useState({});
  const [newSkill, setNewSkill] = useState('');
  const [newInterest, setNewInterest] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const formRef = useRef(null);

  // System fields that are handled specially in the UI
  const systemFields = ['_id', 'id', 'password', 'created_at', 'updated_at', 'is_active', 'token'];
  
  // Known fields that have custom UI components or are handled specially
  const knownFields = ['name', 'email', 'role', 'skills', 'interests', 'experience', 'education', 'goals'];

  useEffect(() => {
    if (authUser) {
      loadUserProfile();
    }
  }, [authUser]);

  const loadUserProfile = async () => {
    try {
      if (!authUser?._id) return;
      
      const response = await api.get(`/api/users/profile/${authUser._id}`);
      if (response.data) {
        setProfile(response.data);
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addSkill = () => {
    if (newSkill.trim() && !(profile.skills || []).includes(newSkill.trim())) {
      setProfile(prev => ({
        ...prev,
        skills: [...(prev.skills || []), newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setProfile(prev => ({
      ...prev,
      skills: (prev.skills || []).filter(skill => skill !== skillToRemove)
    }));
  };

  const addInterest = () => {
    if (newInterest.trim() && !(profile.interests || []).includes(newInterest.trim())) {
      setProfile(prev => ({
        ...prev,
        interests: [...(prev.interests || []), newInterest.trim()]
      }));
      setNewInterest('');
    }
  };

  const removeInterest = (interestToRemove) => {
    setProfile(prev => ({
      ...prev,
      interests: (prev.interests || []).filter(interest => interest !== interestToRemove)
    }));
  };

  // Collect all form fields automatically from the form and state
  const collectFormData = () => {
    const data = {};
    
    if (formRef.current) {
      // Collect all input fields from the form (for uncontrolled components)
      const inputs = formRef.current.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        // Skip buttons, file inputs, and inputs without names
        if (input.type === 'button' || input.type === 'submit' || input.type === 'file' || !input.name) {
          return;
        }
        
        // Handle checkboxes
        if (input.type === 'checkbox') {
          data[input.name] = input.checked;
        }
        // Handle number inputs
        else if (input.type === 'number') {
          const value = input.value;
          data[input.name] = value === '' ? null : parseFloat(value);
        }
        // Handle text inputs, textareas, selects
        else {
          data[input.name] = input.value;
        }
      });
    }

    // Merge with profile state (which includes all fields - known and dynamic)
    // Profile state takes precedence as it's the source of truth for controlled components
    Object.keys(profile).forEach(key => {
      if (!systemFields.includes(key.toLowerCase())) {
        data[key] = profile[key];
      }
    });

    return data;
  };

  const handleSave = async (e) => {
    if (e) {
      e.preventDefault();
    }
    
    setLoading(true);
    setMessage('');

    try {
      // Collect all form data automatically
      const formData = collectFormData();
      
      // Send all data to backend (includes both known and unknown fields)
      const response = await api.put('/api/users/profile', formData);

      if (response.data.success) {
        setMessage('Profile updated successfully!');
        // Reload profile to get any server-side changes and new fields
        await loadUserProfile();
      }
    } catch (error) {
      setMessage(error.response?.data?.error || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Get all dynamic fields (fields from backend that aren't known fields)
  const getDynamicFields = () => {
    return Object.entries(profile || {})
      .filter(([key, value]) => 
        !systemFields.includes(key.toLowerCase()) &&
        !knownFields.includes(key) &&
        shouldDisplayField(key, value)
      );
  };

  // Render a dynamic field based on its type
  const renderDynamicField = (fieldName, value) => {
    const inputType = getInputType(value);
    const humanizedName = humanizeFieldName(fieldName);

    switch (inputType) {
      case 'array':
        return (
          <TextField
            key={fieldName}
            fullWidth
            label={humanizedName}
            name={fieldName}
            value={(value || []).join(', ')}
            onChange={(e) => {
              const arrayValue = e.target.value.split(',').map(item => item.trim()).filter(item => item);
              handleInputChange(fieldName, arrayValue);
            }}
            margin="normal"
            helperText="Separate multiple values with commas"
          />
        );

      case 'boolean':
        return (
          <TextField
            key={fieldName}
            fullWidth
            label={humanizedName}
            name={fieldName}
            type="checkbox"
            checked={value === true}
            onChange={(e) => handleInputChange(fieldName, e.target.checked)}
            margin="normal"
            InputProps={{
              inputProps: { type: 'checkbox' }
            }}
          />
        );

      case 'number':
        return (
          <TextField
            key={fieldName}
            fullWidth
            label={humanizedName}
            name={fieldName}
            type="number"
            value={value || ''}
            onChange={(e) => handleInputChange(fieldName, parseFloat(e.target.value) || 0)}
            margin="normal"
          />
        );

      case 'object':
        // For objects, display as JSON string (can be improved later)
        return (
          <TextField
            key={fieldName}
            fullWidth
            label={humanizedName}
            name={fieldName}
            value={JSON.stringify(value || {})}
            onChange={(e) => {
              try {
                const objValue = JSON.parse(e.target.value);
                handleInputChange(fieldName, objValue);
              } catch (err) {
                // Invalid JSON, just store as string for now
                handleInputChange(fieldName, e.target.value);
              }
            }}
            margin="normal"
            multiline
            rows={2}
            helperText="Enter as JSON object"
          />
        );

      default: // text
        return (
          <TextField
            key={fieldName}
            fullWidth
            label={humanizedName}
            name={fieldName}
            value={String(value || '')}
            onChange={(e) => handleInputChange(fieldName, e.target.value)}
            margin="normal"
          />
        );
    }
  };

  const dynamicFields = getDynamicFields();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profile Management
        </Typography>

        {message && (
          <Alert severity={message.includes('successfully') ? 'success' : 'error'} sx={{ mb: 2 }}>
            {message}
          </Alert>
        )}

        <form ref={formRef} onSubmit={handleSave}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Basic Information
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar sx={{ width: 64, height: 64, mr: 2 }}>
                      {(profile.name || '').charAt(0).toUpperCase()}
                    </Avatar>
                    <Box>
                      <Typography variant="h6">{profile.name || 'User'}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {profile.role || ''}
                      </Typography>
                    </Box>
                  </Box>

                  <TextField
                    fullWidth
                    label="Full Name"
                    name="name"
                    value={profile.name || ''}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    margin="normal"
                  />

                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    value={profile.email || ''}
                    disabled
                    margin="normal"
                  />

                  <TextField
                    fullWidth
                    label="Role"
                    name="role"
                    value={profile.role || ''}
                    disabled
                    margin="normal"
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Skills and Interests */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Skills & Interests
                  </Typography>

                  {/* Skills */}
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Skills
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {(profile.skills || []).map((skill, index) => (
                        <Chip
                          key={index}
                          label={skill}
                          onDelete={() => removeSkill(skill)}
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <TextField
                        size="small"
                        placeholder="Add skill"
                        value={newSkill}
                        onChange={(e) => setNewSkill(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                      />
                      <Button variant="outlined" onClick={addSkill} type="button">
                        Add
                      </Button>
                    </Box>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  {/* Interests */}
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Interests
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {(profile.interests || []).map((interest, index) => (
                        <Chip
                          key={index}
                          label={interest}
                          onDelete={() => removeInterest(interest)}
                          color="secondary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <TextField
                        size="small"
                        placeholder="Add interest"
                        value={newInterest}
                        onChange={(e) => setNewInterest(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInterest())}
                      />
                      <Button variant="outlined" onClick={addInterest} type="button">
                        Add
                      </Button>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Experience and Education */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Professional Information
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Experience"
                        name="experience"
                        multiline
                        rows={4}
                        value={profile.experience || ''}
                        onChange={(e) => handleInputChange('experience', e.target.value)}
                        placeholder="Describe your work experience..."
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Education"
                        name="education"
                        multiline
                        rows={4}
                        value={profile.education || ''}
                        onChange={(e) => handleInputChange('education', e.target.value)}
                        placeholder="Describe your educational background..."
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Career Goals"
                        name="goals"
                        multiline
                        rows={3}
                        value={profile.goals || ''}
                        onChange={(e) => handleInputChange('goals', e.target.value)}
                        placeholder="What are your career goals and aspirations?"
                      />
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Test Field"
                          name="test_field"
                          value={profile.test_field || ''}
                          onChange={(e) => handleInputChange('test_field', e.target.value)}
                        />
                    </Grid>

                    {/* 
                      DYNAMIC FIELDS EXAMPLE:
                      To add a new field, simply add a TextField with name, value, and onChange:
                      
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Phone Number"
                          name="phone_number"
                          value={profile.phone_number || ''}
                          onChange={(e) => handleInputChange('phone_number', e.target.value)}
                        />
                      </Grid>
                      
                      The field will automatically be saved to backend and loaded on next page visit.
                      No need to modify form submission or backend code!
                    */}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Save Button */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ px: 4 }}
                >
                  {loading ? 'Saving...' : 'Save Profile'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Box>
    </Container>
  );
};

export default Profile;
