# Smart Task Manager

A full-stack task management application with AI-powered study assistance. Built with React, FastAPI, and OpenAI integration.

## Features

### Core Features
- **User Authentication** - Secure login and registration system with JWT tokens
- **Task Management** - Create, edit, and track tasks with deadlines and effort levels
- **Calendar View** - Visualize tasks on an interactive calendar (view preference persists)
- **Dark Mode UI** - Modern dark theme throughout the application

### Task Workspace
Each task has a dedicated workspace with:
- **Rich Text Notes** - Auto-saving notes editor
- **File Attachments** - Upload PDFs and images as study materials
- **AI Study Guide** - Generates comprehensive summaries, key points, concepts, action items, and study tips
- **Resource Suggestions** - AI-powered web search for relevant study materials using Perplexity API
- **Assignment Solver** - Upload assignments (PDF/image) and get AI-generated solution approaches based on your notes

### Collaboration
- **Task Sharing** - Share tasks with other users via email
- **Permission Levels** - Choose between view-only or edit access
- **Email Notifications** - Automatic email when someone shares a task with you
- **Deadline Reminders** - Email notifications 1 hour before task deadlines

### Smart Features
- **AI Task Suggestions** - Intelligent task prioritization recommendations
- **PDF Text Extraction** - Automatically extracts text from uploaded PDFs for AI analysis
- **Image Analysis** - Vision AI support for image-based assignments

## Tech Stack

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API requests
- CSS with dark mode design

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite database (PostgreSQL for production)
- JWT authentication
- OpenAI API (GPT-4o-mini) for AI features
- Perplexity API for resource suggestions
- APScheduler for background tasks
- SMTP for email notifications
- PyPDF2 for PDF text extraction

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- OpenAI API key
- Perplexity API key (optional, for resource suggestions)
- Gmail account with App Password (optional, for email notifications)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Arjun-Raje/Smart-Task-Manager.git
cd Smart-Task-Manager
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start the Backend

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes |
| `PERPLEXITY_API_KEY` | Perplexity API key for resource suggestions | No |
| `SMTP_HOST` | SMTP server hostname (default: smtp.gmail.com) | No |
| `SMTP_PORT` | SMTP server port (default: 587) | No |
| `SMTP_USER` | Email address for sending notifications | No |
| `SMTP_PASSWORD` | Email password or app password | No |
| `EMAIL_FROM_NAME` | Sender name in emails (default: Task Manager) | No |
| `FRONTEND_URL` | Frontend URL for email links (default: http://localhost:5173) | No |

### Gmail Setup for Email Notifications

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Create an App Password: Security > App passwords > Select "Mail" > Generate
4. Use the 16-character password as `SMTP_PASSWORD`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get single task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Workspace
- `GET /tasks/{id}/workspace/notes` - Get task notes
- `PUT /tasks/{id}/workspace/notes` - Update task notes
- `GET /tasks/{id}/workspace/attachments` - List attachments
- `POST /tasks/{id}/workspace/attachments` - Upload attachment
- `DELETE /tasks/{id}/workspace/attachments/{attachment_id}` - Delete attachment
- `GET /tasks/{id}/workspace/summary` - Get saved AI summary
- `POST /tasks/{id}/workspace/summary/generate` - Generate new AI summary
- `GET /tasks/{id}/workspace/resources` - Get saved resources
- `POST /tasks/{id}/workspace/resources/generate` - Find new resources
- `GET /tasks/{id}/workspace/assignments` - Get assignment solutions
- `POST /tasks/{id}/workspace/assignments/solve` - Upload and solve assignment
- `DELETE /tasks/{id}/workspace/assignments/{solution_id}` - Delete solution

### Sharing
- `POST /tasks/{id}/share` - Share task with another user
- `GET /tasks/{id}/shares` - List all shares for a task
- `DELETE /tasks/{id}/share/{share_id}` - Revoke share
- `GET /tasks/{id}/my-permission` - Get current user's permission
- `GET /shared-with-me` - List tasks shared with current user

## Project Structure

```
task-manager/
├── backend/
│   ├── auth/              # Authentication logic
│   ├── db/                # Database configuration
│   ├── models/            # SQLAlchemy models
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── task_note.py
│   │   ├── task_attachment.py
│   │   ├── task_summary.py
│   │   ├── task_resource.py
│   │   ├── task_share.py
│   │   └── assignment_solution.py
│   ├── routers/           # API route handlers
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── workspace.py
│   │   └── share.py
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── ai_service.py          # AI summary generation
│   │   ├── resource_service.py    # Resource suggestions
│   │   ├── assignment_service.py  # Assignment solving
│   │   ├── email_service.py       # Email notifications
│   │   └── scheduler_service.py   # Background tasks
│   ├── uploads/           # File upload storage
│   ├── config.py          # App configuration
│   ├── main.py            # FastAPI app entry point
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── auth/          # Authentication context
│   │   ├── components/    # React components
│   │   │   ├── AISummary.tsx
│   │   │   ├── AssignmentSolver.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── NotesEditor.tsx
│   │   │   ├── ResourceSuggestions.tsx
│   │   │   ├── ShareTaskModal.tsx
│   │   │   ├── SharedTasksList.tsx
│   │   │   ├── TaskCalendar.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskList.tsx
│   │   ├── pages/         # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── TaskWorkspace.tsx
│   │   ├── types.ts       # TypeScript types
│   │   └── App.tsx        # Main app component
│   └── package.json
└── README.md
```

## Deployment

### Backend (Production)

1. Use a production ASGI server:
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Set up a reverse proxy (nginx) and HTTPS

3. Use a production database (PostgreSQL recommended):
```bash
pip install psycopg2-binary
# Update database URL in db/database.py
```

4. Configure environment variables for production

### Frontend (Production)

1. Build the production bundle:
```bash
cd frontend
npm run build
```

2. Serve the `dist` folder using a static file server or CDN

### Docker Deployment

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FRONTEND_URL=${FRONTEND_URL}
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/task_manager.db:/app/task_manager.db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## License

MIT License

## Author

Arjun Raje
