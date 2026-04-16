// Milestone Controller - create milestone, get milestones, update milestone status
import Milestone from '../models/milestone.model.js';
import Project from '../models/project.model.js';

const createMilestone = async (req, res) => {
  try {
    const { projectId, title, description, targetDate } = req.body;
    const userId = req.user.id;

    if (!projectId || !title) {
      return res.status(400).json({ error: 'Project ID and title are required' });
    }

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const newMilestone = new Milestone({
      projectId,
      title,
      description,
      targetDate,
      createdBy: userId,
      status: 'active'
    });

    await newMilestone.save();

    res.status(201).json({ message: 'Milestone created successfully', milestone: newMilestone });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getMilestones = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const milestones = await Milestone.find({ projectId })
      .populate('createdBy', 'fullName email')
      .sort({ targetDate: 1 });

    res.status(200).json({ milestones });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const updateMilestoneStatus = async (req, res) => {
  try {
    const { milestoneId } = req.params;
    const { status } = req.body;
    const userId = req.user.id;

    if (!['active', 'completed', 'cancelled'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    const milestone = await Milestone.findById(milestoneId);
    if (!milestone) {
      return res.status(404).json({ error: 'Milestone not found' });
    }

    // Verify user is a project member
    const project = await Project.findById(milestone.projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    milestone.status = status;
    if (status === 'completed') {
      milestone.completedAt = new Date();
    }

    await milestone.save();

    res.status(200).json({ message: 'Milestone status updated successfully', milestone });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { createMilestone, getMilestones, updateMilestoneStatus };
