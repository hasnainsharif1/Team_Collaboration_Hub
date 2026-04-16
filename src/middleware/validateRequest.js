const validateRequest = (schema) => {
  return (req, res, next) => {
    try {
      // Validate body if provided
      if (schema.body) {
        const errors = [];

        for (const field in schema.body) {
          const rule = schema.body[field];
          const value = req.body[field];

          // Check required
          if (rule.required && (value === undefined || value === null || value === '')) {
            errors.push(`${field} is required.`);
            continue;
          }

          // Check type
          if (value !== undefined && value !== null && rule.type) {
            if (typeof value !== rule.type) {
              errors.push(`${field} must be of type ${rule.type}.`);
            }
          }

          // Check minLength
          if (value && rule.minLength && value.length < rule.minLength) {
            errors.push(`${field} must be at least ${rule.minLength} characters.`);
          }

          // Check maxLength
          if (value && rule.maxLength && value.length > rule.maxLength) {
            errors.push(`${field} must not exceed ${rule.maxLength} characters.`);
          }

          // Check pattern
          if (value && rule.pattern && !rule.pattern.test(value)) {
            errors.push(rule.patternMessage || `${field} is invalid.`);
          }
        }

        if (errors.length > 0) {
          return res.status(400).json({ message: 'Validation failed.', errors });
        }
      }

      next();
    } catch (error) {
      return res.status(500).json({ message: 'Validation error.', error: error.message });
    }
  };
};

export default validateRequest;