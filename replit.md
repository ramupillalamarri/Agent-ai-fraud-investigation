# Agentic AI Fraud Investigation Platform

## Project Overview

This repository contains two projects:

1. **`frontend/`** — A Next.js 15 enterprise UI for the fraud investigation platform
2. **`backend/`** — A FastAPI Python backend with agentic AI fraud investigation pipelines

---

## Frontend (`frontend/`)

### Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS v3 + shadcn/ui component library
- **Theme**: Dark-only enterprise theme (forced dark mode via `next-themes`)
- **Linting**: ESLint (Next.js config)
- **Formatting**: Prettier with `prettier-plugin-tailwindcss`

### Running the frontend
```bash
cd frontend && npm run dev   # starts on port 5000
```

The Replit workflow **"Start application"** runs this automatically.

### Key pages
| Route | Description |
|---|---|
| `/` | Redirects to `/dashboard` |
| `/dashboard` | Empty dashboard with KPI cards, activity feed, quick actions |
| `/login` | Enterprise login page (UI only — no auth wired) |

### Folder structure
```
frontend/
├── app/
│   ├── (auth)/login/       # Login page (client component)
│   ├── (dashboard)/        # Dashboard layout + pages
│   ├── globals.css          # Tailwind base + CSS variables
│   └── layout.tsx           # Root layout with ThemeProvider
├── components/
│   ├── layout/              # Sidebar, TopNav
│   └── ui/                  # shadcn/ui components (Button, Card, etc.)
├── hooks/                   # use-sidebar hook
├── lib/utils.ts             # cn() helper + utilities
├── types/index.ts           # Shared TypeScript types
└── public/
```

### Adding new shadcn/ui components
Components live in `frontend/components/ui/`. Add new ones from [ui.shadcn.com](https://ui.shadcn.com) or use the CLI:
```bash
cd frontend && npx shadcn@latest add <component>
```

---

## Backend (`backend/`)

### Stack
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0 async
- **Database**: PostgreSQL (via asyncpg)
- **Auth**: JWT (skeleton)
- **AI Agents**: LLM-powered pipelines (Gemini 1.5 Pro default)

### Running the backend
The backend requires PostgreSQL and an LLM API key. Copy `.env.example` → `.env` and fill in credentials before starting.

```bash
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs` when `DEBUG=true`.

---

## User Preferences
- Enterprise dark theme, no light mode
- No authentication logic in frontend (UI-only forms)
- No mock APIs — connect real backend when ready
- shadcn/ui for all UI components
- Keep frontend and backend in separate directories
