import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import connectDB from './config/database.js';
import initAdmin from './config/initAdmin.js';
import adminRoutes from './routes/admin.routes.js';
import userRoutes from './routes/user.routes.js';
import projectRoutes from './routes/project.routes.js';
import memberRoutes from './routes/member.routes.js';
import taskRoutes from './routes/task.routes.js';
import milestoneRoutes from './routes/milestone.routes.js';
import documentRoutes from './routes/document.routes.js';
import commentRoutes from './routes/comment.routes.js';
import meetingNotesRoutes from './routes/meeting-notes.routes.js';
import checkinRoutes from './routes/checkin.routes.js';
import errorHandler from './middleware/errorHandler.js';
import Admin from './models/admin.model.js';

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/admin', adminRoutes);
app.use('/api/users', userRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/projects', memberRoutes);
app.use('/api/tasks', taskRoutes);
app.use('/api/projects', milestoneRoutes);
app.use('/api/projects', documentRoutes);
app.use('/api/comments', commentRoutes);
app.use('/api/projects', meetingNotesRoutes);
app.use('/api/projects', checkinRoutes);

app.get('/', (req, res) => {
  res.json({ message: 'Team Collaboration Hub backend is running' });
});


// Global error handler (must be last)
app.use(errorHandler);

const PORT = process.env.PORT || 3000;

const startServer = async () => {
  await connectDB();
  await initAdmin();

  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
};

startServer();