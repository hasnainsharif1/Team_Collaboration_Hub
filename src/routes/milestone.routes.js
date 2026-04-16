import express from 'express';
import { createMilestone, getMilestones, updateMilestoneStatus } from '../controllers/milestone.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new milestone
router.post('/', createMilestone);

// Get all milestones for a project
router.get('/:projectId/milestones', getMilestones);

// Update milestone status
router.patch('/:milestoneId/status', updateMilestoneStatus);

export default router;