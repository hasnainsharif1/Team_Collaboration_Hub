import express from 'express';
import {
  createDocument,
  uploadNewVersion,
  reviewDocumentVersion,
  getAllDocuments,
  getSingleDocumentWithVersions
} from '../controllers/document.controller.js';
import authMiddleware from '../middleware/auth.middleware.js';

const router = express.Router();

// All routes require authentication
router.use(authMiddleware);

// Create a new document
router.post('/', createDocument);

// Upload a new version of a document
router.post('/:documentId/version', uploadNewVersion);

// Review a document version (owner only)
router.patch('/:documentId/version/:versionId/review', reviewDocumentVersion);

// Get all documents for a project
router.get('/:projectId/documents', getAllDocuments);

// Get a single document with all versions
router.get('/:documentId', getSingleDocumentWithVersions);

export default router;