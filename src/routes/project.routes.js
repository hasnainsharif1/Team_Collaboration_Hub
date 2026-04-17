import express from 'express';
import {
  createProject,
  getMyProjects,
  getSingleProject,
  generateInviteLink,
  joinViaInviteToken
} from '../controllers/project.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';
import validateRequest from '../middleware/validateRequest.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new project
router.post('/', validateRequest({
  body: {
    name: { required: true, type: 'string', minLength: 1, maxLength: 100 },
    description: { type: 'string', maxLength: 500 }
  }
}), createProject);

// Get all projects for the authenticated user
router.get('/', getMyProjects);

// Get a single project by ID
router.get('/:projectId', validateRequest({
  params: {
    projectId: { required: true, isObjectId: true }
  }
}), getSingleProject);

// Generate invite link for a project (owner only)
router.post('/:projectId/invite', validateRequest({
  params: {
    projectId: { required: true, isObjectId: true }
  }
}), generateInviteLink);

// Join project via invite token
router.post('/join', validateRequest({
  body: {
    token: { required: true, type: 'string', minLength: 32, maxLength: 32 }
  }
}), joinViaInviteToken);

export default router;