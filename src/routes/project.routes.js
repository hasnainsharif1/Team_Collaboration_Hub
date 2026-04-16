import express from 'express';
import {
  createProject,
  getMyProjects,
  getSingleProject,
  generateInviteLink,
  joinViaInviteToken
} from '../controllers/project.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new project
router.post('/', createProject);

// Get all projects for the authenticated user
router.get('/', getMyProjects);

// Get a single project by ID
router.get('/:projectId', getSingleProject);

// Generate invite link for a project (owner only)
router.post('/:projectId/invite', generateInviteLink);

// Join project via invite token
router.post('/join', joinViaInviteToken);

export default router;