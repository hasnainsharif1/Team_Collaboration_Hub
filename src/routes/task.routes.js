import express from 'express';
import { createTask, getTasks, updateTaskStatus, deleteTask } from '../controllers/task.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new task
router.post('/', createTask);

// Get tasks (filtered by project/milestone)
router.get('/', getTasks);

// Update task status
router.patch('/:taskId/status', updateTaskStatus);

// Delete a task
router.delete('/:taskId', deleteTask);

export default router;