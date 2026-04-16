import mongoose from 'mongoose';

const documentSchema = new mongoose.Schema(
  {
    projectId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Project',
      required: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    description: {
      type: String,
      default: '',
      trim: true,
    },
    createdBy: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    latestVersionId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'DocumentVersion',
      default: null,
    },
    versions: {
      type: Number,
      default: 0,
    },
    lastModifiedAt: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true,
  }
);

const Document = mongoose.model('Document', documentSchema);
export default Document;
