// Project Controller - create project, get my projects, get single project, generate invite link, join via invite token
import Project from '../models/project.model.js';
import crypto from 'crypto';

const createProject = async (req, res) => {
  try {
    const { name, description } = req.body;
    const userId = req.user.id; // From auth middleware

    if (!name) {
      return res.status(400).json({ error: 'Project name is required' });
    }

    const newProject = new Project({
      name,
      description,
      owner: userId,
      members: [userId]
    });

    await newProject.save();

    res.status(201).json({
      message: 'Project created successfully',
      project: newProject
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getMyProjects = async (req, res) => {
  try {
    const userId = req.user.id;

    const projects = await Project.find({ members: userId }).populate('owner', 'fullName email');

    res.status(200).json({ projects });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getSingleProject = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    const project = await Project.findById(projectId)
      .populate('owner', 'fullName email')
      .populate('members', 'fullName email');

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Check if user is a member
    if (!project.members.some(m => m._id.toString() === userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    res.status(200).json({ project });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const generateInviteLink = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    const project = await Project.findById(projectId);

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Check if user is project owner
    if (project.owner.toString() !== userId) {
      return res.status(403).json({ error: 'Only project owner can generate invite links' });
    }

    const inviteToken = crypto.randomBytes(32).toString('hex');
    project.inviteToken = inviteToken;
    project.inviteTokenExpiry = new Date(Date.now() + 2 * 24 * 60 * 60 * 1000); // 2 days

    await project.save();

    const inviteLink = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/join?token=${inviteToken}`;

    res.status(200).json({ inviteLink, inviteToken });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const joinViaInviteToken = async (req, res) => {
  try {
    const { token } = req.body;
    const userId = req.user.id;

    if (!token) {
      return res.status(400).json({ error: 'Invite token is required' });
    }

    const project = await Project.findOne({
      inviteToken: token,
      inviteTokenExpiry: { $gt: new Date() }
    });

    if (!project) {
      return res.status(404).json({ error: 'Invalid or expired invite token' });
    }

    // Check if user is already a member
    if (project.members.includes(userId)) {
      return res.status(400).json({ error: 'User is already a member of this project' });
    }

    project.members.push(userId);
    await project.save();

    res.status(200).json({ message: 'Joined project successfully', project });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { createProject, getMyProjects, getSingleProject, generateInviteLink, joinViaInviteToken };
