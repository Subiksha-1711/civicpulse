# CivicPulse — Frontend Prototype

An AI-powered civic intelligence platform frontend, built with React + Vite.

## Tech Stack
- React 19 (JavaScript, no TypeScript)
- Vite
- React Router DOM
- Recharts (charts)
- Lucide React (icons)
- Plain CSS (no Tailwind)

## Getting Started

```bash
npm install
npm run dev
```

Then open the printed local URL (usually http://localhost:5173).

To build for production:

```bash
npm run build
npm run preview
```

## What's inside

- `src/pages/` — all 15 screens (Landing, Report Issue, Issues List, Issue Details,
  AI Deduplication Demo, Dashboard, Analytics, Map View, My Reports, About, Login,
  Signup, Profile, Settings, Notifications, Feedback)
- `src/components/` — reusable UI building blocks (Sidebar, Topbar, IssueCard,
  StatCard, ChartCard, MapView, FilterBar, Badges, Modal, Toast, etc.)
- `src/context/AppContext.jsx` — central app state (issues, auth, notifications,
  settings) backed by `localStorage` so data stays consistent across every page
- `src/data/` — mock dataset: 45 generated civic issues, users, notifications,
  categories/locations

## Notes

- This is a **frontend-only prototype**. There is no backend, database, or real
  AI model — the AI Deduplication Demo and AI Cluster Summary are simulated with
  mock data and timed animations, ready to be wired up to a real backend/ML
  service later.
- Login/Signup create a mock user session stored in `localStorage`
  (`civicpulse_user`). No real authentication occurs.
- Submitting a new issue via **Report an Issue** adds it to the shared issue
  dataset (`civicpulse_issues` in `localStorage`), so it immediately shows up in
  Issues List, Dashboard, My Reports, Analytics, and Map View.
