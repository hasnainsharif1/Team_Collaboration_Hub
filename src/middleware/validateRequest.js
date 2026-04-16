const validateRequest = (schema) => {
  return (req, res, next) => {
    const locations = ['body', 'params', 'query'];
    const errors = [];

    locations.forEach((location) => {
      if (!schema[location]) {
        return;
      }

      const source = req[location];
      const rules = schema[location];

      Object.keys(rules).forEach((field) => {
        const value = source[field];
        const config = rules[field];

        if (config.required && (value === undefined || value === null || value === '')) {
          errors.push({ field, location, message: `${field} is required.` });
          return;
        }

        if (value !== undefined && value !== null) {
          if (config.type && typeof value !== config.type) {
            errors.push({
              field,
              location,
              message: `${field} must be a ${config.type}.`,
            });
          }

          if (config.minLength && typeof value === 'string' && value.length < config.minLength) {
            errors.push({
              field,
              location,
              message: `${field} must be at least ${config.minLength} characters long.`,
            });
          }

          if (config.pattern && typeof value === 'string' && !config.pattern.test(value)) {
            errors.push({
              field,
              location,
              message: config.patternMessage || `${field} has an invalid format.`,
            });
          }
        }
      });
    });

    if (errors.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed.',
        errors,
      });
    }

    next();
  };
};

export default validateRequest;
