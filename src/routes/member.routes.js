import express from 'express';
import { getAllMembers, removeMember } from '../controllers/member.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Get all members of a project
router.get('/:projectId/members', getAllMembers);

// Remove a member from a project (owner only)
router.delete('/:projectId/members/:memberId', removeMember);

export default router;