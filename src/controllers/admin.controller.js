import Admin from '../models/admin.model.js';
import jwt from 'jsonwebtoken';

const generateToken = (adminId) => {
  return jwt.sign(
    { adminId },
    process.env.JWT_SECRET || 'secret',
    { expiresIn: process.env.JWT_EXPIRY || '7d' }
  );
};

export const loginAdmin = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required.' });
    }

    const admin = await Admin.findOne({ email }).select('+password');
    if (!admin) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    const isPasswordValid = await admin.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    const token = generateToken(admin._id);

    return res.status(200).json({
      message: 'Admin logged in successfully.',
      token,
      admin: admin.getProfile(),
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error while logging in.', error: error.message });
  }
};

export const logoutAdmin = async (req, res) => {
  // Since there is no token/session system yet, logout is handled on the frontend.
  // This endpoint is useful as a standard response for a logout action.
  return res.status(200).json({ message: 'Admin logged out successfully.' });
};
