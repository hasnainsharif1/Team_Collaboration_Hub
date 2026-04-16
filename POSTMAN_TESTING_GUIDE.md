# Postman Testing Guide - Team Collaboration Hub API

## Quick Setup

### 1. Import Collection
1. Open Postman
2. Click **Import** → Select **Team_Collaboration_Hub.postman_collection.json**
3. Collection will load with all endpoints

### 2. Configure Environment
The collection uses variables. Set them in Postman:

**Collection Variables** (Click ⚙️ icon next to collection name):
- `BASE_URL` = `http://localhost:3000`
- `TOKEN` = Will be set after login
- Other IDs = Will be set as you create resources

## Testing Flow

### Step 1: Authentication

#### Register a New User
```
POST /api/users/register
Body:
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "1234567890",
  "university": "MIT",
  "department": "Engineering"
}
```
**Response:** Get `token` → Save to `{{TOKEN}}` variable

#### Login User
```
POST /api/users/login
Body:
{
  "email": "john@example.com",
  "password": "password123"
}
```
**Response:** Get `token` → Save to `{{TOKEN}}`

---

### Step 2: Projects

#### Create a Project
```
POST /api/projects
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "name": "Q1 Development Project",
  "description": "Main development project"
}
```
**Response:** Get `project._id` → Save to `{{PROJECT_ID}}`

#### Get My Projects
```
GET /api/projects
Headers: Authorization: Bearer {{TOKEN}}
```
Response shows all projects user is member of

#### Get Single Project
```
GET /api/projects/{{PROJECT_ID}}
Headers: Authorization: Bearer {{TOKEN}}
```

#### Generate Invite Link
```
POST /api/projects/{{PROJECT_ID}}/invite
Headers: Authorization: Bearer {{TOKEN}}
```
**Response:** Get `inviteToken` → Save to `{{INVITE_TOKEN}}`

#### Join Project via Invite
```
POST /api/projects/join
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "token": "{{INVITE_TOKEN}}"
}
```

---

### Step 3: Members

#### Get All Members
```
GET /api/projects/{{PROJECT_ID}}/members
Headers: Authorization: Bearer {{TOKEN}}
```
Response shows all project members with details

#### Remove Member
```
DELETE /api/projects/{{PROJECT_ID}}/members/{{MEMBER_ID}}
Headers: Authorization: Bearer {{TOKEN}}
```
(Requires project owner auth)

---

### Step 4: Milestones

#### Create Milestone
```
POST /api/projects
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "projectId": "{{PROJECT_ID}}",
  "title": "Phase 1 - Foundation",
  "description": "Build core infrastructure",
  "targetDate": "2026-06-30"
}
```
**Response:** Get `milestone._id` → Save to `{{MILESTONE_ID}}`

#### Get Milestones
```
GET /api/projects/{{PROJECT_ID}}/milestones
Headers: Authorization: Bearer {{TOKEN}}
```

#### Update Milestone Status
```
PATCH /api/projects/{{MILESTONE_ID}}/status
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "status": "completed"
}
```
Valid statuses: `active`, `completed`, `cancelled`

---

### Step 5: Tasks

#### Create Task
```
POST /api/tasks
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "projectId": "{{PROJECT_ID}}",
  "title": "Design System Architecture",
  "description": "Create design system",
  "milestoneId": "{{MILESTONE_ID}}",
  "assignedTo": "{{ASSIGNED_USER_ID}}",
  "dueDate": "2026-05-31"
}
```
**Response:** Get `task._id` → Save to `{{TASK_ID}}`

#### Get Tasks
```
GET /api/tasks?projectId={{PROJECT_ID}}&milestoneId={{MILESTONE_ID}}
Headers: Authorization: Bearer {{TOKEN}}
```

#### Update Task Status
```
PATCH /api/tasks/{{TASK_ID}}/status
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "status": "in-progress"
}
```
Valid statuses: `todo`, `in-progress`, `completed`

#### Delete Task
```
DELETE /api/tasks/{{TASK_ID}}
Headers: Authorization: Bearer {{TOKEN}}
```
(Requires creator or owner auth)

---

### Step 6: Documents

#### Create Document
```
POST /api/projects
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "projectId": "{{PROJECT_ID}}",
  "title": "Project Requirements",
  "description": "Main requirements doc"
}
```
**Response:** Get `document._id` → Save to `{{DOCUMENT_ID}}`

#### Upload New Document Version
```
POST /api/projects/{{DOCUMENT_ID}}/version
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "fileUrl": "https://res.cloudinary.com/cloud/image/upload/v1234567890/doc.pdf",
  "fileName": "requirements-v2.pdf",
  "assignedTo": "{{OWNER_ID}}",
  "comment": "Updated requirements"
}
```
**Response:** Get `version._id` → Save to `{{VERSION_ID}}`

#### Review Document Version - Accept
```
PATCH /api/projects/{{DOCUMENT_ID}}/version/{{VERSION_ID}}/review
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "decision": "accept"
}
```
**Effect:** Previous version deleted, new version becomes current

#### Review Document Version - Decline
```
PATCH /api/projects/{{DOCUMENT_ID}}/version/{{VERSION_ID}}/review
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "decision": "decline"
}
```
**Effect:** New version marked declined, previous remains

#### Get All Documents
```
GET /api/projects/{{PROJECT_ID}}/documents
Headers: Authorization: Bearer {{TOKEN}}
```

#### Get Document with Versions
```
GET /api/projects/{{DOCUMENT_ID}}
Headers: Authorization: Bearer {{TOKEN}}
```

---

### Step 7: Comments

#### Add Comment
```
POST /api/comments
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "documentVersionId": "{{VERSION_ID}}",
  "text": "This looks good. One suggestion..."
}
```

#### Get Comments
```
GET /api/comments/{{VERSION_ID}}/comments
Headers: Authorization: Bearer {{TOKEN}}
```

---

### Step 8: Meeting Notes

#### Create Meeting Note
```
POST /api/projects
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "projectId": "{{PROJECT_ID}}",
  "title": "Weekly Standup",
  "content": "Discussed Q2 roadmap and timeline",
  "meetingDate": "2026-04-17",
  "attendees": ["{{USER_ID_1}}", "{{USER_ID_2}}"]
}
```
**Response:** Get `meetingNote._id` → Save to `{{MEETING_NOTE_ID}}`

#### Get All Meeting Notes
```
GET /api/projects/{{PROJECT_ID}}/meeting-notes
Headers: Authorization: Bearer {{TOKEN}}
```

#### Update Meeting Note
```
PATCH /api/projects/{{MEETING_NOTE_ID}}
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "title": "Weekly Standup (Updated)",
  "content": "Updated content here"
}
```

---

### Step 9: Check-ins

#### Submit Weekly Check-in
```
POST /api/projects
Headers: Authorization: Bearer {{TOKEN}}
Body:
{
  "projectId": "{{PROJECT_ID}}",
  "accomplishments": "Completed auth, deployed to staging",
  "challenges": "Database performance issues",
  "nextWeekPlan": "Optimize queries, implement caching"
}
```
**Note:** Only one check-in per user per week

#### Get All Check-ins
```
GET /api/projects/{{PROJECT_ID}}/checkins?userId={{USER_ID}}&week=2026-04-17
Headers: Authorization: Bearer {{TOKEN}}
```

---

## Important Variables to Set

After each successful response, update these variables:

| Variable | How to Get |
|----------|-----------|
| `{{TOKEN}}` | Login/Register response → token |
| `{{PROJECT_ID}}` | Create Project response → project._id |
| `{{DOCUMENT_ID}}` | Create Document response → document._id |
| `{{TASK_ID}}` | Create Task response → task._id |
| `{{MILESTONE_ID}}` | Create Milestone response → milestone._id |
| `{{VERSION_ID}}` | Upload Version response → version._id |
| `{{MEMBER_ID}}` | Get Members response → members[0]._id |
| `{{USER_ID}}` | Login response → user.id |
| `{{ASSIGNED_USER_ID}}` | Any user ID from members list |
| `{{OWNER_ID}}` | Project owner's ID |
| `{{MEETING_NOTE_ID}}` | Create Meeting Note → meetingNote._id |

## Setting Variables in Postman

### Option 1: Manual (Easy)
1. Click ⚙️ icon next to collection name
2. Click Variables tab
3. Paste token, IDs in "Current value" column

### Option 2: Auto (Using Scripts)
In request, go to Tests tab and add:
```javascript
// Set token after login
if (pm.response.code === 200 && pm.response.json().token) {
  pm.collectionVariables.set("TOKEN", pm.response.json().token);
}

// Set project ID after create
if (pm.response.code === 201 && pm.response.json().project) {
  pm.collectionVariables.set("PROJECT_ID", pm.response.json().project._id);
}
```

---

## Error Responses

### 400 - Bad Request
```json
{
  "error": "Project ID and title are required"
}
```
**Fix:** Check required fields

### 401 - Unauthorized
```json
{
  "error": "Access token required"
}
```
**Fix:** Add `Authorization: Bearer {{TOKEN}}` header

### 403 - Forbidden
```json
{
  "error": "Only project owner can..."
}
```
**Fix:** Use owner account, not regular member

### 404 - Not Found
```json
{
  "error": "Project not found"
}
```
**Fix:** Check ID exists, use correct ID

### 409 - Conflict
```json
{
  "error": "User already exists"
}
```
**Fix:** Use different email for registration

---

## Complete Testing Checklist

- [ ] Register user
- [ ] Login user (save token)
- [ ] Create project (save project ID)
- [ ] Get my projects
- [ ] Generate invite link (save token)
- [ ] Create milestone (save milestone ID)
- [ ] Create task (save task ID)
- [ ] Update task status
- [ ] Create document (save document ID)
- [ ] Upload document version (save version ID)
- [ ] Review document - accept
- [ ] Review document - decline
- [ ] Add comment
- [ ] Get comments
- [ ] Create meeting note
- [ ] Update meeting note
- [ ] Submit check-in
- [ ] Get check-ins
- [ ] Get project members
- [ ] Remove member

---

## Tips

1. **Always check response** for new IDs to use in next requests
2. **Token expires after 7 days** - Login again if needed
3. **Project owner only** - Use owner account for special operations
4. **Document workflow** - Upload version first, then review
5. **Check-in limit** - One per user per week per project
6. **Test with multiple users** - Create 2nd user to test collaboration features

---

## API Base Endpoints Summary

```
Authentication:
POST /api/users/register          - Register
POST /api/users/login             - Login
POST /api/users/logout            - Logout
POST /api/admin/login             - Admin login

Projects:
POST   /api/projects              - Create
GET    /api/projects              - Get my projects
GET    /api/projects/:id          - Get single
POST   /api/projects/:id/invite   - Generate invite

Members:
GET    /api/projects/:id/members  - Get all
DELETE /api/projects/:id/members/:memberId - Remove

Tasks:
POST   /api/tasks                 - Create
GET    /api/tasks                 - Get (filtered)
PATCH  /api/tasks/:id/status      - Update status
DELETE /api/tasks/:id             - Delete

Milestones:
POST   /api/projects/:id/milestones  - Create
GET    /api/projects/:id/milestones  - Get
PATCH  /api/projects/:id/status      - Update status

Documents:
POST   /api/projects              - Create
POST   /api/projects/:id/version  - Upload version
PATCH  /api/projects/:id/version/:vid/review - Review
GET    /api/projects/:id/documents - Get all
GET    /api/projects/:id          - Get with versions

Comments:
POST   /api/comments              - Add
GET    /api/comments/:vid/comments - Get

Meeting Notes:
POST   /api/projects              - Create
GET    /api/projects/:id/meeting-notes - Get
PATCH  /api/projects/:id          - Update

Check-ins:
POST   /api/projects              - Submit
GET    /api/projects/:id/checkins - Get
```

---

Happy Testing! 🚀