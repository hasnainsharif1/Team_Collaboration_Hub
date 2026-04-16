// Document Controller - create document, upload new version, get all documents, get single document with versions
// Note: This controller handles document versioning and owner review workflow
import Document from '../models/document.model.js';
import DocumentVersion from '../models/documentVersion.model.js';
import Project from '../models/project.model.js';

const createDocument = async (req, res) => {
  try {
    const { projectId, title, description } = req.body;
    const userId = req.user.id;

    if (!projectId || !title) {
      return res.status(400).json({ error: 'Project ID and title are required' });
    }

    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const newDocument = new Document({
      projectId,
      title,
      description,
      createdBy: userId
    });

    await newDocument.save();

    res.status(201).json({ message: 'Document created successfully', document: newDocument });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const uploadNewVersion = async (req, res) => {
  try {
    const { documentId } = req.params;
    const { fileUrl, fileName, comment, assignedTo } = req.body;
    const userId = req.user.id;

    if (!fileUrl || !fileName) {
      return res.status(400).json({ error: 'File URL and file name are required' });
    }

    const document = await Document.findById(documentId);
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const project = await Project.findById(document.projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const versionNumber = (document.versions || 0) + 1;
    const newVersion = new DocumentVersion({
      documentId,
      versionNumber,
      fileUrl,
      fileName,
      uploadedBy: userId,
      assignedTo,
      comment,
      status: 'pending'
    });

    await newVersion.save();

    // Do not replace the current document version until owner review
    res.status(201).json({ message: 'Document update submitted for review', version: newVersion });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const reviewDocumentVersion = async (req, res) => {
  try {
    const { documentId, versionId } = req.params;
    const { decision } = req.body;
    const userId = req.user.id;

    if (!['accept', 'decline'].includes(decision)) {
      return res.status(400).json({ error: 'Decision must be accept or decline' });
    }

    const document = await Document.findById(documentId);
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const project = await Project.findById(document.projectId);
    if (!project || project.owner.toString() !== userId) {
      return res.status(403).json({ error: 'Only project owner can review document updates' });
    }

    const version = await DocumentVersion.findById(versionId);
    if (!version || version.documentId.toString() !== documentId) {
      return res.status(404).json({ error: 'Document version not found' });
    }

    if (version.status !== 'pending') {
      return res.status(400).json({ error: 'Only pending versions can be reviewed' });
    }

    version.reviewedBy = userId;
    version.reviewedAt = new Date();

    if (decision === 'decline') {
      version.status = 'declined';
      await version.save();
      return res.status(200).json({ message: 'Document update declined', version });
    }

    // Accept the update and replace the current version
    const previousVersionId = document.latestVersionId;

    version.status = 'accepted';
    await version.save();

    document.latestVersionId = version._id;
    document.versions = version.versionNumber;
    document.lastModifiedAt = new Date();
    await document.save();

    if (previousVersionId && previousVersionId.toString() !== versionId) {
      await DocumentVersion.findByIdAndDelete(previousVersionId);
    }

    res.status(200).json({ message: 'Document update accepted', version, document });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getAllDocuments = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const documents = await Document.find({ projectId })
      .populate('createdBy', 'fullName email')
      .populate('latestVersionId')
      .sort({ createdAt: -1 });

    res.status(200).json({ documents });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getSingleDocumentWithVersions = async (req, res) => {
  try {
    const { documentId } = req.params;
    const userId = req.user.id;

    const document = await Document.findById(documentId)
      .populate('createdBy', 'fullName email')
      .populate('latestVersionId');

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    const project = await Project.findById(document.projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const versions = await DocumentVersion.find({ documentId })
      .populate('uploadedBy', 'fullName email')
      .sort({ versionNumber: -1 });

    res.status(200).json({ document, versions });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { createDocument, uploadNewVersion, reviewDocumentVersion, getAllDocuments, getSingleDocumentWithVersions };
