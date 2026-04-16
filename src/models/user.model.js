import mongoose from 'mongoose';
import bcryptjs from 'bcryptjs';

const userSchema = new mongoose.Schema(
  {
    // Basic Information
    firstName: {
      type: String,
      required: true,
      trim: true,
    },

    lastName: {
      type: String,
      required: true,
      trim: true,
    },

    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      match: [/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/, 'Please provide a valid email'],
    },

    password: {
      type: String,
      required: true,
      minlength: 6,
      select: false, // Don't include in queries by default
    },

    // Profile Information
    phone: {
      type: String,
      default: null,
    },

    university: {
      type: String,
      default: null,
    },

    department: {
      type: String,
      default: null,
    },

    // Account Status
    isEmailVerified: {
      type: Boolean,
      default: false,
    },

    // Activity Tracking
    lastActiveAt: {
      type: Date,
      default: Date.now,
    },

    lastLoginAt: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true, // Automatically adds createdAt and updatedAt
  }
);


// Hash password before saving if it's modified
userSchema.pre('save', async function () {
  if (!this.isModified('password')) {
    return;
  }

  try {
    const salt = await bcryptjs.genSalt(10);
    this.password = await bcryptjs.hash(this.password, salt);
  } catch (error) {
    throw error;
  }
});


// Compare password during login
userSchema.methods.comparePassword = async function (passwordToCheck) {
  return await bcryptjs.compare(passwordToCheck, this.password);
};

// Get full name
userSchema.methods.getFullName = function () {
  return `${this.firstName} ${this.lastName}`;
};

// Update last active time
userSchema.methods.updateLastActive = async function () {
  this.lastActiveAt = new Date();
  return await this.save();
};

// Update last login time
userSchema.methods.updateLoginTime = async function () {
  this.lastLoginAt = new Date();
  return await this.save();
};


const User = mongoose.model('User', userSchema);
export default User;
