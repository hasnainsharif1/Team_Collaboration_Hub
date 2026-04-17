import express from 'express';
import rateLimit from 'express-rate-limit';
import { loginAdmin, logoutAdmin } from '../controllers/admin.controller.js';
import validateRequest from '../middleware/validateRequest.js';

const router = express.Router();

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 login attempts per windowMs
  message: 'Too many login attempts, please try again later.',
});

router.post(
  '/login',
  authLimiter,
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
