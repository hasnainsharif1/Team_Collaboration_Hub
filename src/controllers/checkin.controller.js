// Check-in Controller - submit weekly checkin, get all checkins for a project
import CheckIn from '../models/checkin.model.js';
import Project from '../models/project.model.js';

const submitWeeklyCheckIn = async (req, res) => {
  try {
    const { projectId, accomplishments, challenges, nextWeekPlan } = req.body;
    const userId = req.user.id;

    if (!projectId || !accomplishments || !challenges) {
      return res.status(400).json({ error: 'Project ID, accomplishments, and challenges are required' });
    }

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    // Check if check-in already exists for this week
    const startOfWeek = new Date();
    startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay());
    startOfWeek.setHours(0, 0, 0, 0);

    const existingCheckIn = await CheckIn.findOne({
      projectId,
      submittedBy: userId,
      createdAt: { $gte: startOfWeek }
    });

    if (existingCheckIn) {
      return res.status(400).json({ error: 'Check-in already submitted for this week' });
    }

    const newCheckIn = new CheckIn({
      projectId,
      accomplishments,
      challenges,
      nextWeekPlan,
      submittedBy: userId
    });

    await newCheckIn.save();

    res.status(201).json({ message: 'Weekly check-in submitted successfully', checkIn: newCheckIn });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getAllCheckIns = async (req, res) => {
  try {
    const { projectId } = req.params;
    const { userId, week } = req.query;
    const currentUserId = req.user.id;

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(currentUserId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const filter = { projectId };
    if (userId) filter.submittedBy = userId;

    // Filter by week if provided
    if (week) {
      const startDate = new Date(week);
      const endDate = new Date(week);
      endDate.setDate(endDate.getDate() + 7);
      filter.createdAt = { $gte: startDate, $lt: endDate };
    }

    const checkIns = await CheckIn.find(filter)
      .populate('submittedBy', 'fullName email')
      .sort({ createdAt: -1 });

    res.status(200).json({ checkIns });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { submitWeeklyCheckIn, getAllCheckIns };
