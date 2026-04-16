import express from 'express';
import { createMeetingNote, getAllMeetingNotes, updateMeetingNote } from '../controllers/meeting-notes.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new meeting note
router.post('/', createMeetingNote);

// Get all meeting notes for a project
router.get('/:projectId/meeting-notes', getAllMeetingNotes);

// Update a meeting note
router.patch('/:meetingNoteId', updateMeetingNote);

export default router;