// Member Controller - get all members of a project, remove a member
import Project from '../models/project.model.js';
import User from '../models/user.model.js';

const getAllMembers = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    const project = await Project.findById(projectId).populate('members', 'fullName email');

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Check if user is a member
    if (!project.members.some(m => m._id.toString() === userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    res.status(200).json({ members: project.members });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const removeMember = async (req, res) => {
  try {
    const { projectId, memberId } = req.params;
    const userId = req.user.id;

    const project = await Project.findById(projectId);

    if (!project) {
      return res.status(404).json({ error: 'Project not found' });
    }

    // Check if user is project owner
    if (project.owner.toString() !== userId) {
      return res.status(403).json({ error: 'Only project owner can remove members' });
    }

    // Prevent removing the owner
    if (project.owner.toString() === memberId) {
      return res.status(400).json({ error: 'Cannot remove project owner' });
    }

    project.members = project.members.filter(m => m.toString() !== memberId);
    await project.save();

    res.status(200).json({ message: 'Member removed successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { getAllMembers, removeMember };
