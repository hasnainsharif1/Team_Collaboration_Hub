import express from 'express';
import { addComment, getComments } from '../controllers/comment.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Add a comment to a document version
router.post('/', addComment);

// Get all comments for a document version
router.get('/:documentVersionId/comments', getComments);

export default router;