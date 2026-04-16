import mongoose from 'mongoose';
import bcryptjs from 'bcryptjs';

const adminSchema = new mongoose.Schema(
  {
    name: {
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
      select: false,
    },
  },
  {
    timestamps: true,
  }
);

adminSchema.pre('save', async function (next) {
  if (!this.isModified('password')) {
    return next();
  }

  try {
    const salt = await bcryptjs.genSalt(10);
    this.password = await bcryptjs.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

adminSchema.methods.comparePassword = async function (passwordToCheck) {
  return bcryptjs.compare(passwordToCheck, this.password);
};

adminSchema.methods.getProfile = function () {
  const adminObject = this.toObject();
  delete adminObject.password;
  return adminObject;
};

adminSchema.statics.findByEmail = function (email) {
  return this.findOne({ email: email.toLowerCase() });
};

const Admin = mongoose.model('Admin', adminSchema);
export default Admin;
