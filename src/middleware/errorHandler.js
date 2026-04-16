const errorHandler = (err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  const errors = err.errors || null;

  if (process.env.NODE_ENV !== 'production') {
    console.error(err.stack || err);
  }

  return res.status(statusCode).json({
    success: false,
    message,
    errors,
  });
};

export default errorHandler;
