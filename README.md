# Team Collaboration Hub - Backend

A comprehensive backend for a team collaboration platform with project management, document versioning, task tracking, and team communication features.

## Features

- **User Authentication** - Registration, login, JWT tokens
- **Project Management** - Create projects, invite members via tokens
- **Task Management** - Create, update, and track task status
- **Milestone Tracking** - Set and monitor project milestones
- **Document Management** - Upload documents with version control and owner review workflow
- **Comments** - Comment on document versions
- **Meeting Notes** - Record and manage meeting documentation
- **Weekly Check-ins** - Track team progress with weekly updates
- **Member Management** - Add/remove project members

## Tech Stack

- **Node.js** - Runtime
- **Express** - Web framework
- **MongoDB** - Database
- **Mongoose** - ODM
- **JWT** - Authentication
- **Cloudinary** - File storage for documents
- **Multer** - File upload handling
- **Bcryptjs** - Password hashing

## Installation

1. **Clone and install dependencies**
```bash
npm install
```

2. **Configure environment variables**
```bash
cp .env.example .env
```

Update `.env` with:
- MongoDB URI
- JWT_SECRET
- Cloudinary credentials
- Admin email/password

3. **Start the server**

Development:
```bash
npm run dev
```

Production:
```bash
npm start
```

Server runs on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `POST /api/users/logout` - User logout
- `POST /api/admin/login` - Admin login
- `POST /api/admin/logout` - Admin logout

### Projects
- `POST /api/projects` - Create project
- `GET /api/projects` - Get user's projects
- `GET /api/projects/:projectId` - Get project details
- `POST /api/projects/:projectId/invite` - Generate invite link
- `POST /api/projects/join` - Join via invite token

### Members
- `GET /api/projects/:projectId/members` - Get project members
- `DELETE /api/projects/:projectId/members/:memberId` - Remove member

### Tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks` - Get tasks (filtered)
- `PATCH /api/tasks/:taskId/status` - Update task status
- `DELETE /api/tasks/:taskId` - Delete task

### Milestones
- `POST /api/projects/:projectId/milestones` - Create milestone
- `GET /api/projects/:projectId/milestones` - Get milestones
- `PATCH /api/projects/:milestoneId/status` - Update milestone status

### Documents
- `POST /api/documents` - Create document
- `POST /api/documents/:documentId/version` - Upload new version
- `PATCH /api/documents/:documentId/version/:versionId/review` - Review version (owner only)
- `GET /api/documents/:projectId/documents` - Get project documents
- `GET /api/documents/:documentId` - Get document with versions

### Comments
- `POST /api/comments` - Add comment
- `GET /api/comments/:documentVersionId/comments` - Get comments

### Meeting Notes
- `POST /api/projects/:projectId/meeting-notes` - Create meeting note
- `GET /api/projects/:projectId/meeting-notes` - Get meeting notes
- `PATCH /api/projects/:meetingNoteId` - Update meeting note

### Check-ins
- `POST /api/projects/:projectId/checkins` - Submit check-in
- `GET /api/projects/:projectId/checkins` - Get check-ins

## Project Structure

```
src/
├── config/          # Database, Cloudinary, Multer config
├── controllers/     # Business logic for each resource
├── middleware/      # Auth, validation, error handling
├── models/          # Mongoose schemas
├── routes/          # API endpoints
├── utils/           # Helpers, constants, errors
└── server.js        # Express app setup
```

## Middleware

- **authMiddleware** - Verifies JWT token and attaches user to request
- **validateRequest** - Validates request body
- **errorHandler** - Centralized error handling

## Models

- User - User accounts with authentication
- Admin - Admin accounts
- Project - Projects with owner and members
- Task - Tasks within projects
- Milestone - Milestones with status tracking
- Document - Documents with versioning
- DocumentVersion - File versions with review workflow
- Comment - Comments on document versions
- MeetingNote - Meeting documentation
- CheckIn - Weekly progress updates

## Authentication Flow

1. User registers/logs in → receives JWT token
2. Token stored in frontend localStorage
3. Each request includes `Authorization: Bearer <token>`
4. Middleware verifies token and attaches user to request
5. Controllers use `req.user` for authorization checks

## Document Review Workflow

1. Member uploads new document version → status: `pending`
2. System notifies project owner
3. Owner reviews version → `accept` or `decline`
4. If `accept`:
   - Previous version deleted
   - New version becomes current
5. If `decline`:
   - New version marked as `declined`
   - Previous document remains unchanged

## Error Handling

All errors follow standard format:
```json
{
  "error": "Error message",
  "details": [...optional details...]
}
```

HTTP Status Codes:
- 200 - OK
- 201 - Created
- 400 - Bad Request
- 401 - Unauthorized
- 403 - Forbidden
- 404 - Not Found
- 409 - Conflict
- 500 - Server Error

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `MONGODB_URI` - MongoDB connection string
- `JWT_SECRET` - Secret key for JWT signing
- `CLOUDINARY_*` - Cloudinary API credentials
- `ADMIN_*` - Default admin credentials
- `FRONTEND_URL` - Frontend URL for invite links

## Development

```bash
# Install dependencies
npm install

# Run in development mode with auto-reload
npm run dev

# Check for errors
npm test
```

## Notes

- All protected routes require valid JWT token
- Project owners have special permissions (invite, remove members, review documents)
- Documents follow a strict review workflow
- Weekly check-ins have duplicate prevention (one per user per week)

---

Made with ❤️ for Team Collaboration Hub