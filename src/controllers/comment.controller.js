// Comment Controller - add comment on a document version, get comments
import Comment from '../models/comment.model.js';
import DocumentVersion from '../models/documentVersion.model.js';
import Document from '../models/document.model.js';
import Project from '../models/project.model.js';

const addComment = async (req, res) => {
  try {
    const { documentVersionId, text } = req.body;
    const userId = req.user.id;

    if (!documentVersionId || !text) {
      return res.status(400).json({ error: 'Document version ID and text are required' });
    }

    const version = await DocumentVersion.findById(documentVersionId);
    if (!version) {
      return res.status(404).json({ error: 'Document version not found' });
    }

    const document = await Document.findById(version.documentId);
    const project = await Project.findById(document.projectId);

    // Verify user is a project member
    if (!project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const newComment = new Comment({
      documentVersionId,
      text,
      createdBy: userId
    });

    await newComment.save();

    res.status(201).json({ message: 'Comment added successfully', comment: newComment });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getComments = async (req, res) => {
  try {
    const { documentVersionId } = req.params;
    const userId = req.user.id;

    const version = await DocumentVersion.findById(documentVersionId);
    if (!version) {
      return res.status(404).json({ error: 'Document version not found' });
    }

    const document = await Document.findById(version.documentId);
    const project = await Project.findById(document.projectId);

    // Verify user is a project member
    if (!project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const comments = await Comment.find({ documentVersionId })
      .populate('createdBy', 'fullName email')
      .sort({ createdAt: 1 });

    res.status(200).json({ comments });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { addComment, getComments };
