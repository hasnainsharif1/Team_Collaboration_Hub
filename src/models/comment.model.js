import mongoose from 'mongoose';

const commentSchema = new mongoose.Schema(
  {
    documentVersionId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DocumentVersion',
      required: true,
    },
    text: {
      type: String,
      required: true,
      trim: true,
    },
    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
  },
  {
    timestamps: true,
  }
);

const Comment = mongoose.model('Comment', commentSchema);
export default Comment;
