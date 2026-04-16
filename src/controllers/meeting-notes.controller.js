// Meeting Notes Controller - create meeting note, get all meeting notes, update meeting note
import MeetingNote from '../models/meetingNote.model.js';
import Project from '../models/project.model.js';

const createMeetingNote = async (req, res) => {
  try {
    const { projectId, title, content, meetingDate, attendees } = req.body;
    const userId = req.user.id;

    if (!projectId || !title || !content) {
      return res.status(400).json({ error: 'Project ID, title, and content are required' });
    }

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const newMeetingNote = new MeetingNote({
      projectId,
      title,
      content,
      meetingDate,
      attendees,
      createdBy: userId
    });

    await newMeetingNote.save();

    res.status(201).json({ message: 'Meeting note created successfully', meetingNote: newMeetingNote });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const getAllMeetingNotes = async (req, res) => {
  try {
    const { projectId } = req.params;
    const userId = req.user.id;

    // Verify user is a project member
    const project = await Project.findById(projectId);
    if (!project || !project.members.includes(userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const meetingNotes = await MeetingNote.find({ projectId })
      .populate('createdBy', 'fullName email')
      .populate('attendees', 'fullName email')
      .sort({ meetingDate: -1 });

    res.status(200).json({ meetingNotes });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

const updateMeetingNote = async (req, res) => {
  try {
    const { meetingNoteId } = req.params;
    const { title, content, attendees } = req.body;
    const userId = req.user.id;

    const meetingNote = await MeetingNote.findById(meetingNoteId);
    if (!meetingNote) {
      return res.status(404).json({ error: 'Meeting note not found' });
    }

    // Verify user is creator or project owner
    const project = await Project.findById(meetingNote.projectId);
    if (!project || (project.owner.toString() !== userId && meetingNote.createdBy.toString() !== userId)) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    if (title) meetingNote.title = title;
    if (content) meetingNote.content = content;
    if (attendees) meetingNote.attendees = attendees;
    meetingNote.updatedAt = new Date();

    await meetingNote.save();

    res.status(200).json({ message: 'Meeting note updated successfully', meetingNote });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { createMeetingNote, getAllMeetingNotes, updateMeetingNote };
