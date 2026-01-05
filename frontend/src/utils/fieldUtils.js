/**
 * Utility functions for handling dynamic form fields
 */

/**
 * Humanize a field name by converting snake_case or camelCase to Title Case
 * Examples:
 * - phone_number -> Phone Number
 * - emailAddress -> Email Address
 * - favorite_color -> Favorite Color
 */
export const humanizeFieldName = (fieldName) => {
  if (!fieldName) return '';
  
  // Handle snake_case
  let humanized = fieldName.replace(/_/g, ' ');
  
  // Handle camelCase - insert space before uppercase letters
  humanized = humanized.replace(/([a-z])([A-Z])/g, '$1 $2');
  
  // Capitalize first letter of each word
  return humanized
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

/**
 * Check if a field is a system/reserved field that shouldn't be displayed as a regular form field
 */
export const isSystemField = (fieldName) => {
  const systemFields = [
    '_id',
    'id',
    'password',
    'created_at',
    'updated_at',
    'is_active',
    'token',
    'email', // Usually handled separately
    'role', // Usually handled separately
  ];
  return systemFields.includes(fieldName.toLowerCase());
};

/**
 * Check if a field should be displayed in the profile
 * Filters out system fields and complex objects/arrays (except simple arrays)
 */
export const shouldDisplayField = (fieldName, value) => {
  if (isSystemField(fieldName)) {
    return false;
  }
  
  // Don't display null or undefined
  if (value === null || value === undefined) {
    return false;
  }
  
  // Don't display complex objects (only allow simple objects with string values)
  if (typeof value === 'object' && !Array.isArray(value) && value !== null) {
    // Only allow simple objects (not nested complex objects)
    const hasComplexValues = Object.values(value).some(
      v => typeof v === 'object' && v !== null && !Array.isArray(v)
    );
    if (hasComplexValues) {
      return false;
    }
  }
  
  return true;
};

/**
 * Get the input type for a field based on its value
 */
export const getInputType = (value) => {
  if (Array.isArray(value)) {
    return 'array';
  }
  if (typeof value === 'number') {
    return 'number';
  }
  if (typeof value === 'boolean') {
    return 'boolean';
  }
  if (typeof value === 'object' && value !== null) {
    return 'object';
  }
  // Default to text for strings
  return 'text';
};
