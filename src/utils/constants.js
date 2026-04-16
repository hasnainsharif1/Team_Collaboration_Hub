// Task Status
export const TASK_STATUS = {
  TODO: 'todo',
  IN_PROGRESS: 'in-progress',
  COMPLETED: 'completed'
};

// Milestone Status
export const MILESTONE_STATUS = {
  ACTIVE: 'active',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled'
};

// Document Version Status (for review workflow)
export const DOCUMENT_VERSION_STATUS = {
  PENDING: 'pending',
  ACCEPTED: 'accepted',
  DECLINED: 'declined'
};

// HTTP Status Codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500
};

// Error Messages
export const ERROR_MESSAGES = {
  INVALID_CREDENTIALS: 'Invalid email or password',
  USER_EXISTS: 'User already exists',
  USER_NOT_FOUND: 'User not found',
  UNAUTHORIZED: 'Unauthorized',
  PROJECT_NOT_FOUND: 'Project not found',
  TASK_NOT_FOUND: 'Task not found',
  DOCUMENT_NOT_FOUND: 'Document not found',
  INVALID_TOKEN: 'Invalid token',
  TOKEN_EXPIRED: 'Token expired'
};

// Success Messages
export const SUCCESS_MESSAGES = {
  USER_REGISTERED: 'User registered successfully',
  LOGIN_SUCCESS: 'Login successful',
  LOGOUT_SUCCESS: 'Logged out successfully',
  CREATED: 'Created successfully',
  UPDATED: 'Updated successfully',
  DELETED: 'Deleted successfully'
};

// Invite Token Expiry (7 days in milliseconds)
export const INVITE_TOKEN_EXPIRY = 7 * 24 * 60 * 60 * 1000;