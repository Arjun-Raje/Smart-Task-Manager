# Smart Task Manager

A full-stack task management application with AI-powered study assistance. Built with React, FastAPI, and OpenAI integration.

## Features

- **User Authentication** - Secure login and registration system with JWT tokens
- **Task Management** - Create, edit, and track tasks with deadlines and effort levels
- **Calendar View** - Visualize tasks on an interactive calendar
- **Task Workspace** - Dedicated workspace for each task with:
  - Rich text notes with auto-save
  - File attachments (PDFs, images)
  - AI-powered study guide generation
- **AI Study Guide** - Analyzes your notes and PDF attachments to generate:
  - Comprehensive summaries
  - Key points and concepts
  - Action items
  - Study tips
- **Dark Mode** - Toggle between light and dark themes
- **Smart Suggestions** - AI-powered task prioritization

## Tech Stack

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API requests
- CSS with dark mode support

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite databasea
- JWT authentication
- OpenAI API integration
- PyPDF2 for PDF text extraction

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- OpenAI API key

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
pip install fastapi uvicorn sqlalchemy python-jose passlib bcrypt python-multipart PyPDF2 openai python-dotenv

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
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

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key for AI features |

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

## Project Structure

```
task-manager/
├── backend/
│   ├── auth/           # Authentication logic
│   ├── db/             # Database configuration
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic (AI service)
│   ├── uploads/        # File upload storage
│   ├── config.py       # App configuration
│   ├── main.py         # FastAPI app entry point
│   └── .env            # Environment variables
├── frontend/
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   ├── types.ts    # TypeScript types
│   │   └── App.tsx     # Main app component
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
