const validateRequest = (schema) => {
  return (req, res, next) => {
    try {
      const errors = [];

      // Validate body if provided
      if (schema.body) {
        validateFields(req.body, schema.body, errors, 'body');
      }

      // Validate params if provided
      if (schema.params) {
        validateFields(req.params, schema.params, errors, 'params');
      }

      // Validate query if provided
      if (schema.query) {
        validateFields(req.query, schema.query, errors, 'query');
      }

      if (errors.length > 0) {
        return res.status(400).json({ message: 'Validation failed.', errors });
      }

      next();
    } catch (error) {
      return res.status(500).json({ message: 'Validation error.', error: error.message });
    }
  };
};

const validateFields = (data, rules, errors, source) => {
  for (const field in rules) {
    const rule = rules[field];
    const value = data[field];

    // Check required
    if (rule.required && (value === undefined || value === null || value === '')) {
      errors.push(`${field} in ${source} is required.`);
      continue;
    }

    // Skip further validation if value is not provided and not required
    if (value === undefined || value === null || value === '') {
      continue;
    }

    // Check type
    if (rule.type) {
      if (typeof value !== rule.type) {
        errors.push(`${field} in ${source} must be of type ${rule.type}.`);
        continue;
      }
    }

    // Check minLength
    if (rule.minLength && value.length < rule.minLength) {
      errors.push(`${field} in ${source} must be at least ${rule.minLength} characters.`);
    }

    // Check maxLength
    if (rule.maxLength && value.length > rule.maxLength) {
      errors.push(`${field} in ${source} must not exceed ${rule.maxLength} characters.`);
    }

    // Check pattern
    if (rule.pattern && !rule.pattern.test(value)) {
      errors.push(rule.patternMessage || `${field} in ${source} is invalid.`);
    }

    // Check enum
    if (rule.enum && !rule.enum.includes(value)) {
      errors.push(`${field} in ${source} must be one of: ${rule.enum.join(', ')}.`);
    }

    // Check isObjectId (for MongoDB ObjectIds)
    if (rule.isObjectId && !/^[0-9a-fA-F]{24}$/.test(value)) {
      errors.push(`${field} in ${source} must be a valid ObjectId.`);
    }
  }
};

export default validateRequest;