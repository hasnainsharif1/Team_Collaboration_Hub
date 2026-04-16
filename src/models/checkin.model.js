import mongoose from 'mongoose';

const checkInSchema = new mongoose.Schema(
  {
    projectId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Project',
      required: true,
    },
    accomplishments: {
      type: String,
      required: true,
      trim: true,
    },
    challenges: {
      type: String,
      required: true,
      trim: true,
    },
    nextWeekPlan: {
      type: String,
      default: '',
      trim: true,
    },
    submittedBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
  },
  {
    timestamps: true,
  }
);

const CheckIn = mongoose.model('CheckIn', checkInSchema);
export default CheckIn;
