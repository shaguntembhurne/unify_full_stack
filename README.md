# Unify Hub

A modern Django web app that unifies campus life — news, projects, notifications, and a central calendar — with a built-in AI assistant.

## Highlights
- Unified auth and profiles with roles (Student/Teacher)
- Newsfeed: posts, announcements, polls with likes/comments
- Projects: discover/join projects and manage membership
- Notifications: live bell dropdown with read/unread state
- Teacher-only Analytics page (render-only)
- Central Unify Calendar (FullCalendar) with campus events
- AI Assistant: local RAG via Ollama + ChromaDB
- Global chat widget available on every page

## Tech Stack
- Django 5, SQLite (dev)
- TailwindCSS (CDN), Chart.js (analytics)
- Ollama (llama3) + nomic-embed-text for embeddings
- ChromaDB for vector storage (persistent)

## Getting Started

1) Clone and setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional
```

2) Seed sample data (optional)
```bash
python manage.py seed_university_data
```

3) Run the app
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000/

## AI Setup (Optional but recommended)
The AI assistant uses a local Ollama server and ChromaDB for RAG.

- Install Ollama and pull models:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```
- Start Ollama (if not running):
```bash
ollama serve
```
- Build the vector index from existing content:
```bash
python manage.py ai_reindex
```
- Try the CLI helpers:
```bash
python manage.py test_ai_chat
python manage.py ask_news_today "How many interesting news are there today?"
```

## Key Commands
- `python manage.py seed_university_data` — create demo users, news, and projects
- `python manage.py ai_reindex` — rebuild AI index
- `python manage.py test_ai_chat` — quick RAG sanity check
- `python manage.py ask_news_today "<question>"` — Q&A over today’s news

## App Structure
- `premitive`: auth, profile, notifications, landing, navbar, analytics route
- `news`: posts, announcements, polls, social endpoints
- `projects`: project listing, join, membership
- `ai`: Ollama + Chroma services, views, signals, management commands

## Important Routes
- `/` — Landing page (with How It Works section `/#how-it-works`)
- `/news/` — News hub
- `/projects/` — Projects hub
- `/calendar/` — Unify Calendar
- `/profile/` — Your profile
- `/analytics/teachers/` — Teacher Analytics (link visible to teachers)

## Development Notes
- Templates share a common `base.html` (navbar + chat)
- The calendar page uses FullCalendar and matches the site’s neubrutalist style
- The navbar shows a teacher-only Analytics link when `profile.role == 'teacher'`
- Notifications dropdown auto-fetches and marks-as-read on open
- Auth page provides both login and simple email-based signup (email as username)

## Screenshots (optional)
You can add screenshots here (landing, news, projects, calendar, chat widget, notifications).

## Contributing
PRs welcome! For major changes, please open an issue first to discuss what you’d like to change.

## License
This project is for educational/demo use. Add a LICENSE file if you want a specific license.
