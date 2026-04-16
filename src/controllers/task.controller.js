// Task Controller - create task, get tasks, update task status, delete task
import Task from '../models/task.model.js';
import Project from '../models/project.model.js';

const createTask = async (req, res) => {
  try {
    const { projectId, title, description, milestoneId, assignedTo, dueDate } = req.body;
    const userId = req.user.id;

    if (!projectId || !title) {
      return res.status(400).json({ error: 'Project ID and title are required' });
    }

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'User Unauthorized' });
    }

    const newTask = new Task({
      projectId,
      title,
      description,
      milestoneId,
      assignedTo,
      dueDate,
      createdBy: userId,
      status: 'todo'
    });

    await newTask.save();

    res.status(201).json({ message: 'Task created successfully', task: newTask });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getTasks = async (req, res) => {
  try {
    const { projectId, milestoneId } = req.query;
    const userId = req.user.id;

    // Verify user is a project member
    if (projectId) {
      const project = await Project.findById(projectId);
      if (!project || !project.members.includes(userId)) {
        return res.status(403).json({ error: 'Unauthorized' });
      }
    }

    const filter = {};
    if (projectId) filter.projectId = projectId;
    if (milestoneId) filter.milestoneId = milestoneId;

    const tasks = await Task.find(filter)
      .populate('assignedTo', 'fullName email')
      .populate('createdBy', 'fullName email');

    res.status(200).json({ tasks });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const updateTaskStatus = async (req, res) => {
  try {
    const { taskId } = req.params;
    const { status } = req.body;
    const userId = req.user.id;

    if (!['todo', 'in-progress', 'completed'].includes(status)) {
      return res.status(400).json({ error: 'Invalid status' });
    }

    const task = await Task.findById(taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Verify user is a project member
    const project = await Project.findById(task.projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    task.status = status;
    if (status === 'completed') {
      task.completedAt = new Date();
    }

    await task.save();

    res.status(200).json({ message: 'Task status updated successfully', task });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const deleteTask = async (req, res) => {
  try {
    const { taskId } = req.params;
    const userId = req.user.id;

    const task = await Task.findById(taskId);
    if (!task) {
      return res.status(404).json({ error: 'Task not found' });
    }

    // Verify user is project owner or task creator
    const project = await Project.findById(task.projectId);
    if (!project || (project.owner.toString() !== userId && task.createdBy.toString() !== userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    await Task.findByIdAndDelete(taskId);

    res.status(200).json({ message: 'Task deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { createTask, getTasks, updateTaskStatus, deleteTask };
