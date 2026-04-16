import express from 'express';
import { submitWeeklyCheckIn, getAllCheckIns } from '../controllers/checkin.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Submit a weekly check-in
router.post('/', submitWeeklyCheckIn);

// Get all check-ins for a project
router.get('/:projectId/checkins', getAllCheckIns);

export default router;