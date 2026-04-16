import express from 'express';
import { loginAdmin, logoutAdmin } from '../controllers/admin.controller.js';
import validateRequest from '../middleware/validateRequest.js';

const router = express.Router();

router.post(
  '/login',
  validateRequest({
    body: {
      email: {
        required: true,
        type: 'string',
        pattern: /^\S+@\S+\.\S+$/,
        patternMessage: 'Please provide a valid email.',
      },
      password: { required: true, type: 'string' },
    },
  }),
  loginAdmin
);

router.post('/logout', logoutAdmin);

export default router;
