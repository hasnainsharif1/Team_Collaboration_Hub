import User from '../models/user.model.js';

export const registerUser = async (req, res) => {
  try {
    const { firstName, lastName, email, password, phone, university, department } = req.body;

    if (!firstName || !lastName || !email || !password) {
      return res.status(400).json({ message: 'First name, last name, email, and password are required.' });
    }

    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ message: 'A user with this email already exists.' });
    }

    const user = new User({ firstName, lastName, email, password, phone, university, department });
    await user.save();

    return res.status(201).json({
      message: 'User registered successfully.',
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        phone: user.phone,
        university: user.university,
        department: user.department,
      },
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error during registration.', error: error.message });
  }
};

export const loginUser = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required.' });
    }

    const user = await User.findOne({ email }).select('+password');
    if (!user) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) {
      return res.status(401).json({ message: 'Invalid email or password.' });
    }

    await user.updateLastLoginTime();

    return res.status(200).json({
      message: 'Login successful.',
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        phone: user.phone,
        university: user.university,
        department: user.department,
        lastLoginAt: user.lastLoginAt,
      },
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error during login.', error: error.message });
  }
};

export const getUserProfile = async (req, res) => {
  try {
    const { userId } = req.params;
    const user = await User.findById(userId);

    if (!user) {
      return res.status(404).json({ message: 'User not found.' });
    }

    return res.status(200).json({
      user: {
        id: user._id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        phone: user.phone,
        university: user.university,
        department: user.department,
        lastActiveAt: user.lastActiveAt,
        lastLoginAt: user.lastLoginAt,
      },
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error while fetching user.', error: error.message });
  }
};
